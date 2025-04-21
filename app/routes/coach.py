from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy import text
from app import engine

coach_bp = Blueprint('coach', __name__, url_prefix='/coach')

# ========== STEP 1: Input CoachID ==========
@coach_bp.route('/', methods=['GET', 'POST'])
def coach_login():
    if request.method == 'POST':
        coach_id = request.form.get('coach_id')
        if not coach_id:
            flash("Coach ID is required")
            return redirect(url_for('coach.coach_login'))
        session['coach_id'] = coach_id
        return redirect(url_for('coach.dashboard'))
    return render_template('coach/login.html')


# ========== STEP 2: Coach Dashboard ==========
@coach_bp.route('/dashboard')
def dashboard():
    coach_id = session.get('coach_id')
    if not coach_id:
        return redirect(url_for('coach.coach_login'))
    return render_template('coach/dashboard.html', coach_id=coach_id)


# ========== STEP 3: Create Group ==========
@coach_bp.route('/group/create', methods=['GET', 'POST'])
def create_group():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        coach_id = session.get('coach_id')

        if name and address and coach_id:
            query = text("""
                INSERT INTO Group_ (Name, Address, CoachID)
                VALUES (:name, :address, :coach_id)
            """)
            with engine.connect() as conn:
                conn.execute(query, {"name": name, "address": address, "coach_id": coach_id})
                conn.commit()
            return redirect(url_for('coach.list_groups'))

    return render_template('coach/create_group.html')


# ========== STEP 4: List and Manage Groups ==========
@coach_bp.route('/groups')
def list_groups():
    coach_id = session.get('coach_id')
    query = text("""
        SELECT GroupID, Name, Address FROM Group_
        WHERE CoachID = :coach_id
    """)
    with engine.connect() as conn:
        groups = conn.execute(query, {"coach_id": coach_id}).fetchall()
    return render_template('coach/groups.html', groups=groups)


# ========== STEP 5: View / Add Swimmers to a Group ==========
@coach_bp.route('/group/<int:group_id>/swimmers', methods=['GET', 'POST'])
def manage_swimmers(group_id):
    if request.method == 'POST':
        if 'add' in request.form:
            swimmer_id = request.form.get('swimmer_id')
            if swimmer_id:
                query = text("""
                    UPDATE Swimmer SET GroupID = :group_id
                    WHERE SwimmerID = :swimmer_id
                """)
                with engine.connect() as conn:
                    conn.execute(query, {"group_id": group_id, "swimmer_id": swimmer_id})
                    conn.commit()
        elif 'remove' in request.form:
            swimmer_id = request.form.get('swimmer_id')
            if swimmer_id:
                query = text("""
                    UPDATE Swimmer SET GroupID = NULL
                    WHERE SwimmerID = :swimmer_id
                """)
                with engine.connect() as conn:
                    conn.execute(query, {"swimmer_id": swimmer_id})
                    conn.commit()

    query_swimmers = text("""
        SELECT SwimmerID, Name, Surname FROM Swimmer
        WHERE GroupID = :group_id
    """)
    query_available = text("""
        SELECT SwimmerID, Name, Surname FROM Swimmer
        WHERE GroupID IS NULL
    """)
    with engine.connect() as conn:
        swimmers = conn.execute(query_swimmers, {"group_id": group_id}).fetchall()
        available = conn.execute(query_available).fetchall()

    return render_template('coach/manage_swimmers.html', group_id=group_id, swimmers=swimmers, available=available)


# ========== STEP 6: Delete Group ==========
@coach_bp.route('/group/<int:group_id>/delete', methods=['POST'])
def delete_group(group_id):
    query = text("DELETE FROM Group_ WHERE GroupID = :group_id")
    with engine.connect() as conn:
        conn.execute(query, {"group_id": group_id})
        conn.commit()
    return redirect(url_for('coach.list_groups'))


# ========== STEP 7: Apply / Cancel for Swim Sessions ==========
@coach_bp.route('/swim/apply', methods=['GET', 'POST'])
def apply_swim():
    coach_id = session.get('coach_id')

    if request.method == 'POST':
        swim_id = request.form.get('swim_id')
        if 'apply' in request.form:
            query = text("UPDATE Swim SET CoachID = :coach_id WHERE SwimID = :swim_id AND CoachID IS NULL")
        elif 'cancel' in request.form:
            query = text("UPDATE Swim SET CoachID = NULL WHERE SwimID = :swim_id AND CoachID = :coach_id")
        with engine.connect() as conn:
            conn.execute(query, {"coach_id": coach_id, "swim_id": swim_id})
            conn.commit()

    query_unassigned = text("""
        SELECT s.SwimID, s.Distance, s.Duration,
               e.Name AS EventName,
               ts.StartTime AS StartTime,
               ts.EndTime AS EndTime,
               f.Name AS FacilityName
        FROM Swim s
        JOIN Event e ON s.EventID = e.EventID
        JOIN Timeslot ts ON e.TimeslotID = ts.TimeslotID
        JOIN Facility f ON ts.FacilityID = f.FacilityID
        WHERE s.CoachID IS NULL
    """)

    query_mine = text("""
        SELECT s.SwimID, s.Distance, s.Duration,
               e.Name AS EventName,
               ts.StartTime AS StartTime,
               ts.EndTime AS EndTime,
               f.Name AS FacilityName
        FROM Swim s
        JOIN Event e ON s.EventID = e.EventID
        JOIN Timeslot ts ON e.TimeslotID = ts.TimeslotID
        JOIN Facility f ON ts.FacilityID = f.FacilityID
        WHERE s.CoachID = :coach_id
    """)

    with engine.connect() as conn:
        unassigned = conn.execute(query_unassigned).fetchall()
        mine = conn.execute(query_mine, {"coach_id": coach_id}).fetchall()

    return render_template('coach/apply_swim.html', unassigned=unassigned, mine=mine)

