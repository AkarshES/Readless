from . import app, db
from flask.ext.mongoengine import DoesNotExist, ValidationError
from flask import Response, request, render_template, redirect, url_for, flash, jsonify
from flask.ext.login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Article, Feed, Subscription, NotAFeed

@app.route('/show_db_name')
def test_config():
    '''just a test, to be removed later'''
    return Response(app.config['MONGODB_DB'], mimetype='text/plain')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """all logic to check whether a user exists and log him in"""
    error = None
    if request.method == 'POST':
        try:
            user = User.objects.get(email = request.form['email'])
            if check_password_hash(user.password_hash, request.form['password']) is True:
                login_user(user)
                return redirect(url_for('index'))
            else:
                error = 'Incorrect Password'
        except DoesNotExist:
            error = 'User with this email id does not exist'
    return render_template('login.html', error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        new_user = User(\
                        email = request.form['email']\
                        , name = request.form['name']\
                        , password_hash = generate_password_hash(request.form['password'])\
                        )
        try:
            new_user.save(safe = True, force_insert=True)#waits for result and forces inserts
            flash('successfully signed up')
            return redirect(url_for('login'))
        except db.NotUniqueError:
            error = 'User with this email id already exists'
        except ValidationError as e:
            if e.errors.get('email'):
                error = 'Invalid email'
            elif e.errors.get('name'):
                error = 'Invalid name'
            else:
                error = 'A validation error occured'
    return render_template('signup.html', error=error)

@app.route('/index')
def index():
    return render_template('index.html')
