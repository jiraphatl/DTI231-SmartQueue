from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data for testing
users = {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            return "Login successful! Welcome, {}!".format(username)
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        retype_password = request.form['retype_password']

        if username in users:
            return "Username already exists. Please choose another one."
        if password != retype_password:
            return "Passwords do not match. Please try again."

        users[username] = password
        return redirect(url_for('login'))

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)