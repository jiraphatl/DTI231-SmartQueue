from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Mock Database
users = {"admin": {"password": "admin123", "role": "admin"}}
# Format: {"username": {"password": "password", "role": "role"}}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            if users[username]['role'] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('user'))
        else:
            flash("Invalid credentials!")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('signup'))
        if username in users:
            flash("Username already exists!")
            return redirect(url_for('signup'))
        users[username] = {"password": password, "role": "user"}
        flash("Account created successfully!")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html', users=users)

@app.route('/user')
def user():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    return render_template('user.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

