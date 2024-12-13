# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from reservation_system import ReservationSystem

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For flash messages

# Create a global reservation system instance
reservation_system = ReservationSystem()

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from reservation_system import ReservationSystem
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For flash messages

# Create a global reservation system instance
reservation_system = ReservationSystem()

@app.route('/')
def index():
    return render_template('index.html')

def validate_booking_details(details):
    """
    Validate booking details
    
    Args:
        details (dict): Booking details to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Name validation
    if not details['name'] or len(details['name']) < 2:
        return False, "Please enter a valid name"
    
    # Email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, details['email']):
        return False, "Please enter a valid email address"
    
    # Phone validation (basic)
    phone_regex = r'^\+?1?\d{9,15}$'
    if not re.match(phone_regex, details['phone']):
        return False, "Please enter a valid phone number"
    
    # People validation
    if details['people'] not in ['2', '3', '4']:
        return False, "Please select a valid number of people"
    
    # Date validation (ensure future date)
    import datetime
    try:
        booking_date = datetime.datetime.strptime(details['date'], '%Y-%m-%d').date()
        if booking_date < datetime.date.today():
            return False, "Please select a future date"
    except ValueError:
        return False, "Invalid date format"
    
    # Time validation
    if not details['time']:
        return False, "Please select a time"
    
    return True, ""

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

@app.route('/booking_success/<booking_id>')
def booking_success(booking_id):
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

if __name__ == '__main__':
    app.run(debug=True)