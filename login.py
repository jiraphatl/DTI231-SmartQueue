from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Mock database using a dictionary
user_data = {}

def add_user(username, password):
    if username in user_data:
        return False, "Username already exists"
    else:
        user_data[username] = password
        return True, "User added successfully"

@app.route('/')
def home():
    return "Welcome to the Home Page!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in user_data and user_data[username] == password:
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        success, message = add_user(username, password)
        if success:
            flash('Sign up successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
