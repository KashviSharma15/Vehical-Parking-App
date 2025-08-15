from flask import Flask, render_template, redirect, url_for, request, session, flash
from controller.database import db
from controller.config import Config
from controller.auto_admin import create_auto_admin
from controller.models import User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timezone

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()
    create_auto_admin()

def create_parking_spots(lot_id, capacity):
    for _ in range(capacity):
        spot = ParkingSpot(lot_id=lot_id, status='A')  
        db.session.add(spot)
    db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

# registeration

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash("Email already exists!")
            return redirect(url_for('register'))

        user = User(email=email, username=full_name, password=password, is_admin=False)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

# login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash("Login successful!", "success")

            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# admin
#admin-dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    total_users = User.query.filter_by(is_admin=False).count()

    return render_template('admin_dashboard.html',total_lots=total_lots,total_spots=total_spots,available_spots=available_spots,
                            occupied_spots=occupied_spots,total_users=total_users)

@app.route('/admin/parking-lots')
def admin_parking_lots():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    lots = ParkingLot.query.all()
    return render_template('manage_lots.html', lots=lots)

@app.route('/admin/parking-lot/create', methods=['GET', 'POST'])
def create_parking_lot():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['prime_location_name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price = float(request.form['price_per_unit'])
        capacity = int(request.form['max_spots'])

        new_lot = ParkingLot(prime_location_name=name,address=address,pin_code=pin_code,
                                price_per_unit=price,max_spots=capacity)
        db.session.add(new_lot)
        db.session.commit()

        create_parking_spots(new_lot.id, capacity)

        flash("Parking lot created successfully!", "success")
        return redirect(url_for('admin_parking_lots'))

    return render_template('create_parking_lot.html')

@app.route('/admin/parking-lot/<int:lot_id>', methods=['GET', 'POST'])
def view_parking_lot(lot_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.prime_location_name = request.form['prime_location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_unit = float(request.form['price_per_unit'])
        db.session.commit()
        flash("Parking lot updated successfully!", "success")
        return redirect(url_for('admin_parking_lots'))

    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template('edit_parking_lot.html', lot=lot, spots=spots)

@app.route('/admin/parking-lots/edit/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.prime_location_name = request.form['name']
        lot.address = request.form['location']
        lot.pin_code = request.form['pin_code']
        lot.price_per_unit = float(request.form['price_per_unit'])
        lot.max_spots = int(request.form['capacity'])

        db.session.commit()
        return redirect(url_for('admin_parking_lots'))

    return render_template('edit_parking_lot.html', lot=lot)

@app.route('/admin/parking-lot/delete/<int:lot_id>', methods=['POST'])
def delete_parking_lot(lot_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted successfully!", "success")
    return redirect(url_for('admin_parking_lots'))

@app.route('/admin/parking-lot/<int:lot_id>/view')
def view_parking_lot_detail(lot_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template('view_parking_lots.html', lot=lot, spots=spots)


#user-dashboard

@app.route('/user/dashboard')
def user_dashboard():
    if not session.get('user_id'):
        return redirect('/login')

    user = User.query.get(session['user_id'])
    reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.parking_timestamp.desc()).all()
    current_reservations = [r for r in reservations if r.leaving_timestamp is None]
    past_reservations = [r for r in reservations if r.leaving_timestamp is not None]

    current_spot = current_reservations[0].spot if current_reservations else None
    total_current_reservations = len(current_reservations)

    total_minutes = 0
    total_cost = 0
    reservation_history = []

    for r in past_reservations:
        if r.parking_timestamp and r.leaving_timestamp and r.spot and r.spot.lot:
            duration_minutes = int((r.leaving_timestamp - r.parking_timestamp).total_seconds() // 60)
            cost_per_unit = r.spot.lot.price_per_unit or 0  
            cost = (duration_minutes * cost_per_unit)//60
            total_minutes += duration_minutes
            total_cost += cost

            reservation_history.append({'spot_id': r.spot.id,'lot_name': r.spot.lot.prime_location_name,'parking_time': r.parking_timestamp,
                'leaving_time': r.leaving_timestamp,'duration': duration_minutes,'cost': cost})
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    time = f"{hours}h {minutes}m"

    return render_template('user_dashboard.html',user=user,total_current_reservations=total_current_reservations,
                            current_spot=current_spot,past_reservations_count=len(past_reservations),total_time=time,
                            total_cost=round(total_cost, 2),reservation_history=reservation_history)

@app.route('/user/available-lots')
def view_available_lots():

    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        total_spots = len(lot.spots)
        available_spots = sum(1 for spot in lot.spots if spot.status == 'A')
        data.append({'id': lot.id,'prime_location_name': lot.prime_location_name,'address': lot.address,
                'available_spots': available_spots,'total_spots': total_spots})

    return render_template('available_lots.html', lots=data)

@app.route('/user/reserve/<int:lot_id>')
def reserve_spot(lot_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session['user_id']
    lot = ParkingLot.query.get_or_404(lot_id)

    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if not available_spot:
        flash('No available spots in this lot.', 'danger')
        return redirect(url_for('view_available_lots'))

    available_spot.status = 'O'

    reservation = Reservation(spot_id=available_spot.id,user_id=user_id,parking_timestamp=datetime.now(timezone.utc),cost_per_unit=lot.price_per_unit)
    
    db.session.add(reservation)
    db.session.commit()
    return redirect(url_for('view_user_reservations'))  


@app.route('/admin/users')
def view_all_users():
    users = User.query.all()
    for user in users:
        latest = (Reservation.query.filter_by(user_id=user.id, leaving_timestamp=None)
    .order_by(Reservation.parking_timestamp.desc()).first())

        user.latest_reservation = latest  
    return render_template('users.html', users=users)


@app.route('/user/reservations')
def view_user_reservations():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session['user_id']
    reservations = Reservation.query.filter_by(user_id=user_id)\
        .order_by(Reservation.parking_timestamp.desc()).all()

    return render_template('view_reservations.html', reservations=reservations)

@app.route('/end-reservation/<int:reservation_id>', methods=['POST'])
def end_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != session.get('user_id') and not session.get('is_admin'):
        return "Unauthorized", 403

    if reservation.leaving_timestamp is None:
        reservation.leaving_timestamp = datetime.now(timezone.utc)
        reservation.spot.status = 'A'  
        db.session.commit()
    
    return redirect(url_for('view_user_reservations'))

#logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#reservation details
@app.route('/admin/reservations')
def view_all_reservations():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).all()
    return render_template('admin_all_reservations.html', reservations=reservations)

if __name__ == '__main__':
    app.run(debug=True, port=5001)