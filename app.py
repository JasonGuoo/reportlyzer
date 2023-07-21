from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# load envs from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") 
app.config['SECRET_KEY'] = 'N2G4Zx27gMqLX8j3ys1IcV8Q'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, Role

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])  
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash password
        hashed_pw = generate_password_hash(password, method='sha256')
        
        # Create new user
        new_user = User(username=username, password=hashed_pw, role_id=user_role.id) 
        
        # Add user to db
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/create_role', methods=['GET', 'POST'])
@login_required
def create_role():
    if current_user.role_id != admin_role.id:
        flash('Only admins can create roles')
        return redirect(url_for('index')) 

    if request.method == 'POST':
        name = request.form['name']
        
        new_role = Role(name=name)
        db.session.add(new_role)
        db.session.commit()

        return redirect(url_for('roles'))

    return render_template('create_role.html')

@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
   # Check role 
   # Get form data
   # Hash password
   # Create user
   # Add to db

   return redirect(url_for('users'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])  
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)

    if request.method == 'POST':
        # Get form data
        # Update user
        
        db.session.commit()
        return redirect(url_for('users'))

    return render_template('edit_user.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)