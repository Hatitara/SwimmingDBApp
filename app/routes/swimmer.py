from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import text
from app import engine
from datetime import datetime

swimmer_bp = Blueprint('swimmer', __name__)

@swimmer_bp.route('/')
def swimmer_home():
    return render_template('swimmer/home.html')

@swimmer_bp.route("/register", methods=["GET", "POST"])
def register_swimmer():
    if request.method == "POST":
        name = request.form['name']
        surname = request.form['surname']
        gender = request.form['gender']
        date_of_birth = request.form['date_of_birth']

        QUERY = text("""
            INSERT INTO Swimmer (Name, Surname, Gender, DateOfBirth)
            VALUES (:name, :surname, :gender, :date_of_birth);
        """)
        with engine.connect() as conn:
            conn.execute(
                QUERY,
                {
                    "name": name,
                    "surname": surname,
                    "gender": gender,
                    "date_of_birth": date_of_birth,
                }
            )
            conn.commit()
        return redirect("/swimmer")

    return render_template("swimmer/register.html")

@swimmer_bp.route('/group')
def swimmer_group():
    swimmer_id = request.args.get('swimmer_id')
    if swimmer_id is None:
        return "Swimmer ID is required", 400

    query = text("""
        SELECT sg.name AS group_name, c.name AS coach_name
        FROM Swimmer s
        JOIN Group_ sg ON s.GroupID = sg.GroupID
        JOIN Coach c ON sg.CoachID = c.CoachID
        WHERE s.SwimmerID = :value
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"value" : swimmer_id}).fetchone()
        conn.commit()

    if result:
        return render_template('swimmer/group.html', result=result, swimmer_id=swimmer_id)
    else:
        return "Swimmer not found", 404

@swimmer_bp.route('/schedule')
def swimmer_schedule():
    swimmer_id = request.args.get('swimmer_id')
    if swimmer_id is None:
        return "Swimmer ID is required", 400
    
    query = text("""
        SELECT e.Name AS event_name, t.StartTime AS start, t.EndTime AS end, f.Name AS facility
        FROM Swimmer s
        JOIN Group_ sg ON s.GroupID = sg.GroupID
        JOIN EventSwimmer es ON s.SwimmerID = es.SwimmerID
        JOIN Event e ON es.EventID = e.EventID
        JOIN Timeslot t ON e.TimeslotID = t.TimeslotID
        JOIN Facility f ON t.FacilityID = f.FacilityID
        WHERE s.SwimmerID = :swimmer_id
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, {"swimmer_id": swimmer_id}).fetchall()
        conn.commit()
    
    return render_template('swimmer/schedule.html', schedule=rows, swimmer_id=swimmer_id)


from datetime import datetime

@swimmer_bp.route('/performance', methods=['GET', 'POST'])
def swimmer_performance():
    swimmer_id = request.args.get('swimmer_id')
    if swimmer_id is None:
        return "Swimmer ID is required", 400    

    query = text("""
        SELECT e.name AS event_name, r.Length AS length, r.Time AS time, s.Style AS style
        FROM Result r
        JOIN Event e ON r.EventID = e.EventID
        JOIN Style s ON r.StyleID = s.StyleID
        WHERE r.SwimmerID = :swimmer_id
    """)
    with engine.connect() as conn:
        results = conn.execute(query, {"swimmer_id": swimmer_id}).fetchall()
        conn.commit()

    registration_query = text("""
        SELECT e.Name AS event_name, t.StartTime, e.EventID
        FROM Event e
        JOIN Timeslot t ON e.TimeslotID = t.TimeslotID
        JOIN EventSwimmer es ON es.EventID = e.EventID
        WHERE es.SwimmerID = :swimmer_id
    """)
    with engine.connect() as conn:
        registered_events = conn.execute(registration_query, {"swimmer_id": swimmer_id}).fetchall()
        conn.commit()

    today = datetime.today()
    past_events = []
    upcoming_events = []

    for event in registered_events:
        event_time = event.StartTime
        if event_time < today:
            past_events.append(event)
        else:
            upcoming_events.append(event)

    if request.method == 'POST':
        cancel_event_id = request.form.get('cancel_event_id')
        swimmer_id = request.form.get('swimmer_id')
        if cancel_event_id and swimmer_id:
            cancel_query = text("""
                DELETE FROM EventSwimmer
                WHERE EventID = :event_id AND SwimmerID = :swimmer_id
            """)
            with engine.connect() as conn:
                conn.execute(cancel_query, {"event_id": cancel_event_id, "swimmer_id": swimmer_id})
                conn.commit()
            return redirect(url_for('swimmer.swimmer_performance', swimmer_id=swimmer_id))

    return render_template('swimmer/performance.html', results=results, swimmer_id=swimmer_id, past_events=past_events, upcoming_events=upcoming_events)


@swimmer_bp.route('/register_event', methods=['GET', 'POST'])
def register_event():
    swimmer_id = request.args.get('swimmer_id')
    if not swimmer_id:
        return "Swimmer ID is required", 400

    query = text("""
        SELECT e.EventID, e.Name AS event_name, t.StartTime
        FROM Event e
        JOIN Timeslot t ON e.TimeslotID = t.TimeslotID
        WHERE t.StartTime > NOW()  -- Show only future events
    """)
    with engine.connect() as conn:
        events = conn.execute(query).fetchall()
        conn.commit()

    if request.method == 'POST':
        event_id = request.form.get('event_id')
        if event_id:
            register_query = text("""
                INSERT INTO EventSwimmer (EventID, SwimmerID)
                VALUES (:event_id, :swimmer_id)
            """)
            with engine.connect() as conn:
                conn.execute(register_query, {"event_id": event_id, "swimmer_id": swimmer_id})
                conn.commit()

            return redirect(url_for('swimmer.swimmer_performance', swimmer_id=swimmer_id))

    return render_template('swimmer/register_event.html', events=events, swimmer_id=swimmer_id)

