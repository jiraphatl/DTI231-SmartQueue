from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # เปลี่ยนเป็น key ที่ปลอดภัย

# Mock Database with hashed password
users = {
    "admin": {"password": generate_password_hash("admin123"), "role": "admin"},
    # อาจจะมีผู้ใช้เพิ่มเติม
}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # ตรวจสอบ username และ password
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            session['role'] = users[username]['role']
            
            # ถ้า role เป็น admin ไปหน้า admin
            if users[username]['role'] == 'admin':
                return redirect(url_for('admin'))
            
            # ถ้า role เป็น user ไปหน้า index
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password!", "error")
    
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # ตรวจสอบว่ารหัสผ่านทั้งสองตรงกันหรือไม่
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('signup'))
        
        # ตรวจสอบว่า username มีอยู่ในฐานข้อมูลหรือยัง
        if username in users:
            flash("Username already exists!", "error")
            return redirect(url_for('signup'))
        
        # แฮชรหัสผ่านก่อนที่จะเก็บไว้ในฐานข้อมูล
        users[username] = {"password": generate_password_hash(password), "role": "user"}
        flash("Account created successfully!", "success")
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')
    
if __name__ == '__main__':
    app.run(debug=True)

