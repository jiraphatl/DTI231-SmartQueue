# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from reservation_system import ReservationSystem

app = Flask(__name__)

# Initialize reservation system
reservation_system = ReservationSystem()

@app.route('/')
def index():
    """
    Render the main page
    """
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book_table():
    """
    Handle table booking request
    """
    # Collect form data
    user_info = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'people_count': request.form.get('people_count'),
        'time': request.form.get('time'),
        'date': request.form.get('date')
    }
    
    # Add reservation
    reservation_id = reservation_system.add_reservation(user_info)
    
    # Redirect with reservation confirmation
    return jsonify({
        'status': 'success', 
        'message': 'Reservation successful!', 
        'reservation_id': reservation_id
    })

@app.route('/status/<reservation_id>')
def reservation_status(reservation_id):
    """
    Check reservation status
    """
    status = reservation_system.get_reservation_status(reservation_id)
    
    if not status:
        return jsonify({'status': 'error', 'message': 'Reservation not found'})
    
    return jsonify(status)

@app.route('/cancel/<reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    """
    Cancel a specific reservation
    """
    result = reservation_system.cancel_reservation(reservation_id)
    
    if result:
        return jsonify({'status': 'success', 'message': 'Reservation cancelled'})
    else:
        return jsonify({'status': 'error', 'message': 'Reservation not found'})

if __name__ == '__main__':
    app.run(debug=True)