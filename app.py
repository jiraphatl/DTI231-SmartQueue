from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from reservation_system import ReservationSystem
import re

app = Flask(__name__)
app.secret_key = 'secret_key'  

reservation_system = ReservationSystem()

users = {
    "admin": {"password": "admin123", "email": "admin@example.com"}
}

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            flash('Login successful!', 'success')

            # Check if the logged-in user is admin
            if username == "admin":
                return redirect(url_for('admin'))  # Redirect to admin page if admin
            return redirect(url_for('index'))  # Redirect to index for regular users
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/admin')
def admin():
    # Check if the user is logged in and is an admin
    if 'username' not in session or session['username'] != 'admin':
        flash('Access denied! Only admin users can access this page.', 'error')
        return redirect(url_for('login'))  # Redirect to login if not admin

    # Render the admin page
    return render_template('admin.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if username in users:
            flash('Username already exists', 'error')
        else:
            users[username] = {"password": password, "email": email}
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book_table():
    # Collect booking details from form
    booking_details = {
        'name': request.form.get('name', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
        'people': request.form.get('people', ''),
        'date': request.form.get('date', ''),
        'time': request.form.get('time', '')
    }
    
    # Validate booking details
    is_valid, error_message = validate_booking_details(booking_details)
    
    if not is_valid:
        # If validation fails, flash error and redirect back
        flash(error_message, 'error')
        return redirect(url_for('index') + '#booking')
    
    try:
        # Add booking to reservation system
        booking_id = reservation_system.enqueue_booking(booking_details)
        
        # Redirect to the success page with booking details
        return redirect(url_for('booking_success', booking_id=booking_id))
    
    except Exception as e:
        # Handle any unexpected errors
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index') + '#booking')


    booking = reservation_system.user_bookings.get(booking_id)
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('index'))
    return render_template('success.html', booking=booking)

@app.route('/all_bookings')
def all_bookings():
    bookings = reservation_system.get_all_bookings()  # Retrieve all bookings
    return jsonify(bookings)

@app.route('/next_booking')
def next_booking():
    # Peek at the next booking
    next_booking = reservation_system.peek_next_booking()
    return render_template('next_booking.html', booking=next_booking)

@app.route('/process_next_booking')
def process_next_booking():
    # Process (dequeue) the next booking
    processed_booking = reservation_system.dequeue_booking()
    if processed_booking:
        flash(f'Booking {processed_booking["booking_id"]} processed', 'success')
    else:
        flash('No bookings to process', 'error')
    return redirect(url_for('index'))

def validate_booking_details(details):
    if not details['name'] or len(details['name']) < 2:
        return False, "Please enter a valid name"

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, details['email']):
        return False, "Please enter a valid email address"

    phone_regex = r'^\+?1?\d{9,15}$'
    if not re.match(phone_regex, details['phone']):
        return False, "Please enter a valid phone number"

    if details['people'] not in ['2', '3', '4']:
        return False, "Please select a valid number of people"

    import datetime
    try:
        booking_date = datetime.datetime.strptime(details['date'], '%Y-%m-%d').date()
        if booking_date < datetime.date.today():
            return False, "Please select a future date"
    except ValueError:
        return False, "Invalid date format"

    if not details['time']:
        return False, "Please select a time"

    return True, ""


    booking_details = {
        'name': request.form.get('name', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
        'people': request.form.get('people', ''),
        'date': request.form.get('date', ''),
        'time': request.form.get('time', '')
    }

    is_valid, error_message = validate_booking_details(booking_details)

    if not is_valid:
        flash(error_message, 'error')
        return redirect(url_for('index') + '#booking')

    try:
        booking_id = reservation_system.enqueue_booking(booking_details)
        return redirect(url_for('booking_success', booking_id=booking_id))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index') + '#booking')

@app.route('/booking_success/<booking_id>')
def booking_success(booking_id):
    booking = reservation_system.user_bookings.get(booking_id)
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('index'))
    return render_template('success.html', booking=booking)

@app.route('/admin/queue', methods=['GET'])
def admin_queue():
    if 'username' not in session or session['username'] != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    all_bookings = reservation_system.get_all_bookings()
    next_booking = reservation_system.peek_next_booking()

    return render_template('admin_queue.html', bookings=all_bookings, next_booking=next_booking)

@app.route('/admin/table_availability', methods=['GET'])
def admin_table_availability():
    if 'username' not in session or session['username'] != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    table_availability = [
        {"type": "1 person", "available": len([b for b in reservation_system.booking_queue if reservation_system.user_bookings[b]['people'] == '1']), "total": 30},
        {"type": "2-4 persons", "available": len([b for b in reservation_system.booking_queue if reservation_system.user_bookings[b]['people'] in ['2', '3', '4']]), "total": 30}
    ]

    return render_template('admin_table_availability.html', table_availability=table_availability)


@app.route('/admin/update_table/<table_type>', methods=['POST'])
def update_table(table_type):
    if 'username' not in session or session['username'] != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    table_mapping = {
        "1 person": "1",
        "2-4 persons": ["2", "3", "4"]
    }

    for booking_id in list(reservation_system.booking_queue):
        booking = reservation_system.user_bookings.get(booking_id)
        if booking and booking['people'] in table_mapping.get(table_type, []):
            reservation_system.dequeue_booking()  # Dequeue the booking
            flash(f"Booking {booking_id} processed for {table_type}.", 'success')
            return redirect(url_for('admin_table_availability'))

    flash(f"No bookings available for {table_type}.", 'error')
    return redirect(url_for('admin_table_availability'))


@app.route('/admin/cancel_booking/<booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'username' not in session or session['username'] != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    success = reservation_system.cancel_booking(booking_id)
    if success:
        flash(f"Booking {booking_id} canceled successfully.", 'success')
    else:
        flash(f"Booking {booking_id} not found.", 'error')

    return redirect(url_for('admin_queue'))

if __name__ == '__main__':
    app.run(debug=True)
