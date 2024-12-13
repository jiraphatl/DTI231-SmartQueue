from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from queue import Queue

app = Flask(__name__)
app.secret_key = 'your_very_secret_restaurant_key_2024!'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Data Structures
class User(UserMixin):
    def __init__(self, username, password):
        self.id = username  # LoginManager expects `id` attribute
        self.username = username
        self.password = password

class Table:
    def __init__(self, table_id, capacity):
        self.table_id = table_id
        self.capacity = capacity
        self.is_booked = False
        self.booking = None

class Booking:
    def __init__(self, booking_id, customer_name, time_slot, table_id):
        self.booking_id = booking_id
        self.customer_name = customer_name
        self.time_slot = time_slot
        self.table_id = table_id

# In-memory storage
users = {}  # Hash Table for user data: {username: User}
tables = [Table(table_id=i, capacity=4) for i in range(1, 11)]  # List of 10 tables
bookings = Queue()  # Queue for bookings (FIFO)

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def home():
    return render_template('index.html', tables=tables)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)  # Hash table lookup
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:  # Check if username exists in hash table
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        users[username] = User(username, hashed_password)  # Add to hash table
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/book/<int:table_id>', methods=['GET', 'POST'])
@login_required
def book_table(table_id):
    table = next((t for t in tables if t.table_id == table_id), None)
    if not table:
        flash('Table not found!', 'danger')
        return redirect(url_for('home'))
    if table.is_booked:
        flash('This table is already booked.', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        time_slot = request.form['time_slot']
        booking = Booking(
            booking_id=bookings.qsize() + 1,  # Booking ID based on queue size
            customer_name=current_user.username,
            time_slot=time_slot,
            table_id=table_id
        )
        table.is_booked = True
        table.booking = booking
        bookings.put(booking)  # Add to queue
        flash('Table booked successfully!', 'success')
        return redirect(url_for('queue', booking_id=booking.booking_id))
    return render_template('book_table.html', table=table)

@app.route('/queue/<int:booking_id>')
@login_required
def queue(booking_id):
    booking_list = list(bookings.queue)  # Access queue as a list for display
    booking = next((b for b in booking_list if b.booking_id == booking_id), None)
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('home'))
    return render_template('queue.html', booking=booking, queue_position=booking_list.index(booking) + 1)

@app.route('/my_bookings')
@login_required
def my_bookings():
    user_bookings = [b for b in list(bookings.queue) if b.customer_name == current_user.username]
    return render_template('my_bookings.html', bookings=user_bookings)

if __name__ == "__main__":
    app.run(debug=True)
