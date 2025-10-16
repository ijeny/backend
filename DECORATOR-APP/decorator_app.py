from flask import Flask, render_template, redirect, url_for,request, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'pas1234'

#decorator untuk mengecek apakah pengguna sudah login
def LoginRequired(f):
    @wraps(f)
    def DecoratedFunction(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return DecoratedFunction

#halaman login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #cek username dan password (misalnya, username: admin, password: password123)
        if username == 'admin' and password == 'password123':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
        
    return render_template('login.html')

#halaman dashboard (hanya bisa diakses jika login)
@app.route('/dashboard')
@LoginRequired
def dashboard():
    return render_template('dashboard.html')

#halaman logout
@app.route('/logout')
@LoginRequired
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)