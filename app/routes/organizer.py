from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy import text
from app import engine

organizer_bp = Blueprint('organizer', __name__, url_prefix='/organizer')

@organizer_bp.route('/')
@organizer_bp.route('/dashboard')
def dashboard():
    return render_template('organizer/dashboard.html')

@organizer_bp.route('/events')
def view_events():
    with engine.connect() as conn:
        events = conn.execute(text("""
            SELECT e.EventID, e.Name, e.Type, f.Name AS FacilityName, t.StartTime, t.EndTime
            FROM Event e
            JOIN Timeslot t ON e.TimeslotID = t.TimeslotID
            JOIN Facility f ON t.FacilityID = f.FacilityID
            ORDER BY e.EventID DESC
        """)).fetchall()
    return render_template('organizer/events.html', events=events)

@organizer_bp.route('/events/new', methods=['GET', 'POST'])
def create_event():
    with engine.connect() as conn:
        if request.method == 'POST':
            name = request.form['name']
            type_ = request.form['type']
            facility_id = request.form['facility_id']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            existing = conn.execute(text("""
                SELECT COUNT(*) FROM Timeslot
                WHERE FacilityID = :facility_id AND (
                    (StartTime < :end_time AND EndTime > :end_time) OR
                    (StartTime < :start_time AND EndTime > :start_time) OR
                    (StartTime >= :start_time AND EndTime <= :end_time)
                )
            """), {
                "facility_id": facility_id,
                "start_time": start_time,
                "end_time": end_time
            }).scalar()
            conn.commit()

            if existing == 0:
                conn.execute(text("""
                    INSERT INTO Timeslot (FacilityID, StartTime, EndTime)
                    VALUES (:facility_id, :start_time, :end_time)
                """), {
                    "facility_id": facility_id,
                    "start_time": start_time,
                    "end_time": end_time
                })

                timeslot_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

                conn.execute(text("""
                    INSERT INTO Event (Name, Type, TimeslotID)
                    VALUES (:name, :type, :timeslot_id)
                """), {
                    "name": name,
                    "type": type_,
                    "timeslot_id": timeslot_id
                })

                conn.commit()

            return redirect(url_for('organizer.view_events'))

        facilities = conn.execute(text("SELECT * FROM Facility")).fetchall()
        return render_template('organizer/create_event.html', facilities=facilities)

@organizer_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    with engine.begin() as conn:
        if request.method == 'POST':
            name = request.form['name']
            type_ = request.form['type']
            start_time = request.form['start_time']
            end_time = request.form['end_time']

            timeslot_info = conn.execute(text("""
                SELECT t.TimeslotID, t.FacilityID
                FROM Event e
                JOIN Timeslot t ON e.TimeslotID = t.TimeslotID
                WHERE e.EventID = :event_id
            """), {"event_id": event_id}).fetchone()

            timeslot_id = timeslot_info.TimeslotID
            facility_id = timeslot_info.FacilityID

            conflict = conn.execute(text("""
                SELECT 1 FROM Timeslot
                WHERE FacilityID = :facility_id
                  AND TimeslotID != :timeslot_id
                  AND (
                        (:start_time < EndTime AND :end_time > StartTime)
                      )
            """), {
                "facility_id": facility_id,
                "timeslot_id": timeslot_id,
                "start_time": start_time,
                "end_time": end_time
            }).fetchone()

            if conflict:
                flash("The updated timeslot conflicts with another timeslot in the same facility.", "danger")

                event = conn.execute(text("""
                    SELECT e.*, t.StartTime, t.EndTime, t.TimeslotID
                    FROM Event e
                    JOIN Timeslot t ON e.TimeslotID = t.TimeslotID
                    WHERE e.EventID = :event_id
                """), {"event_id": event_id}).fetchone()

                swimmers = conn.execute(text("""
                    SELECT s.SwimmerID, s.Name, s.Surname
                    FROM Swimmer s
                    JOIN EventSwimmer se ON se.SwimmerID = s.SwimmerID
                    WHERE se.EventID = :event_id
                """), {"event_id": event_id}).fetchall()

                return render_template('organizer/edit_event.html',
                                       event=event,
                                       swimmers=swimmers)

            conn.execute(text("""
                UPDATE Event
                SET Name = :name, Type = :type
                WHERE EventID = :event_id
            """), {
                "name": name,
                "type": type_,
                "event_id": event_id
            })

            conn.execute(text("""
                UPDATE Timeslot
                SET StartTime = :start_time, EndTime = :end_time
                WHERE TimeslotID = :timeslot_id
            """), {
                "start_time": start_time,
                "end_time": end_time,
                "timeslot_id": timeslot_id
            })

            conn.commit()
            return redirect(url_for('organizer.view_events'))

        event = conn.execute(text("""
            SELECT e.*, t.StartTime, t.EndTime, t.TimeslotID
            FROM Event e
            JOIN Timeslot t ON e.TimeslotID = t.TimeslotID
            WHERE e.EventID = :event_id
        """), {"event_id": event_id}).fetchone()

        swimmers = conn.execute(text("""
            SELECT s.SwimmerID, s.Name, s.Surname
            FROM Swimmer s
            JOIN EventSwimmer se ON se.SwimmerID = s.SwimmerID
            WHERE se.EventID = :event_id
        """), {"event_id": event_id}).fetchall()

        return render_template('organizer/edit_event.html',
                               event=event,
                               swimmers=swimmers)


@organizer_bp.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT TimeslotID FROM Event WHERE EventID = :event_id"), {
            "event_id": event_id
        }).fetchone()
        if result is not None:
            timeslot_id = result[0]
            conn.execute(text("DELETE FROM Timeslot WHERE TimeslotID = :timeslot_id"), {
                "timeslot_id": timeslot_id
            })
            conn.commit()
    return redirect(url_for('organizer.view_events'))


@organizer_bp.route('/events/<int:event_id>/swims')
def manage_swims(event_id):
    with engine.connect() as conn:
        swims = conn.execute(text("""
            SELECT s.SwimID, s.Distance, s.Duration, c.Name AS CoachName, st.Style
            FROM Swim s
            LEFT JOIN Coach c ON s.CoachID = c.CoachID
            JOIN Style st ON s.StyleID = st.StyleID
            WHERE s.EventID = :event_id
        """), {"event_id": event_id}).fetchall()
    return render_template('organizer/manage_swims.html', swims=swims, event_id=event_id)


@organizer_bp.route('/events/<int:event_id>/swims/new', methods=['GET', 'POST'])
def add_swim(event_id):
    with engine.connect() as conn:
        if request.method == 'POST':
            distance = request.form['distance']
            duration = request.form['duration']
            style_id = request.form['style_id']
            conn.execute(text("""
                INSERT INTO Swim (Distance, Duration, EventID, StyleID)
                VALUES (:distance, :duration, :event_id, :style_id)
            """), {
                "distance": distance,
                "duration": duration,
                "event_id": event_id,
                "style_id": style_id
            })
            conn.commit()
            return redirect(url_for('organizer.manage_swims', event_id=event_id))

        event = conn.execute(text("""
            SELECT * FROM Event WHERE EventID = :event_id
        """), {"event_id": event_id}).fetchone()
        coaches = conn.execute(text("SELECT * FROM Coach")).fetchall()
        styles = conn.execute(text("SELECT * FROM Style")).fetchall()
        conn.commit()
        return render_template('organizer/add_swim.html', coaches=coaches, styles=styles, event_id=event_id, event=event)

@organizer_bp.route('/swims/<int:swim_id>/delete', methods=['POST'])
def delete_swim(swim_id):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM Swim WHERE SwimID = :swim_id"), {
            "swim_id": swim_id
        })
        conn.commit()
    return redirect(request.referrer or url_for('organizer.view_events'))

@organizer_bp.route('/events/<int:event_id>/swimmers/remove/<int:swimmer_id>', methods=['POST'])
def remove_swimmer(event_id, swimmer_id):
    with engine.connect() as conn:
        conn.execute(text("""
            DELETE FROM EventSwimmer
            WHERE EventID = :event_id AND SwimmerID = :swimmer_id
        """), {
            "event_id": event_id,
            "swimmer_id": swimmer_id
        })
        conn.commit()
    return redirect(request.referrer or url_for('organizer.view_events'))

@organizer_bp.route('/swims/<int:swim_id>/remove-coach', methods=['POST'])
def remove_coach(swim_id):
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE Swim SET CoachID = NULL WHERE SwimID = :swim_id
        """), {
            "swim_id": swim_id
        })
        conn.commit()
    return redirect(request.referrer or url_for('organizer.view_events'))

@organizer_bp.route('/swims/<int:swim_id>/edit', methods=['GET', 'POST'])
def edit_swim(swim_id):
    with engine.begin() as conn:
        if request.method == 'POST':
            distance = request.form['distance']
            duration = request.form['duration']
            style_id = request.form['style_id']
            coach_id = request.form.get('coach_id')

            conn.execute(text("""
                UPDATE Swim
                SET Distance = :distance,
                    Duration = :duration,
                    StyleID = :style_id,
                    CoachID = :coach_id
                WHERE SwimID = :swim_id
            """), {
                "distance": distance,
                "duration": duration,
                "style_id": style_id,
                "coach_id": coach_id,
                "swim_id": swim_id
            })

            event = conn.execute(text("""
                SELECT e.EventID FROM Swim s
                JOIN Event e ON s.EventID = e.EventID
                WHERE s.SwimID = :swim_id
            """), {"swim_id": swim_id}).fetchone()
            return redirect(request.args.get('next') or url_for('organizer.manage_swims', event_id=event.EventID))

        swim = conn.execute(text("""
            SELECT * FROM Swim WHERE SwimID = :swim_id
        """), {"swim_id": swim_id}).fetchone()

        styles = conn.execute(text("SELECT * FROM Style")).fetchall()
        coaches = conn.execute(text("SELECT * FROM Coach")).fetchall()

    return render_template('organizer/edit_swim.html',
                           swim=swim,
                           styles=styles,
                           coaches=coaches)
