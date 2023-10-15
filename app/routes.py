from flask import render_template, session, redirect, url_for, request, flash
from flask_login import login_user, login_required, login_manager
from app import app, coffee_data, db, User

# Initialize the counter on the first request
@app.before_request
def before_request():
    if 'counter' not in session:
        session['counter'] = 0

# Define a route for the homepage
@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

# Define a route for the about page
@app.route('/about')
def about():
    return render_template('about.html')

# Create routes for login and registration
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please try again.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

# Define a route for counter
@app.route('/counter')
@login_required
def counter():
    hot_cold_options = ["Hot", "Cold"]
    drink_type_options = [
        "Americano", "Latte", "Flat white", "Cold brew", "Shaken espresso", 
        "Brewed coffee", "Brewed pike", "Brewed dark", "Chai", 
        "Black tea", "Green tea", "Passion tea", "Refresher", 
        "Frappuccino", "Creme Frappuccino"
    ]
    drink_size_options = ["Short", "Tall", "Grande", "Venti", "Trenta"]

    return render_template('counter.html', counter=session['counter'], hot_cold_options=hot_cold_options, drink_type_options=drink_type_options, drink_size_options=drink_size_options)

@app.route('/reset')
@login_required
def reset():
    session['counter'] = 0
    return redirect(url_for('counter'))

@app.route('/process', methods=['POST'])
@login_required
def process():
    hot_cold = request.form.get('hot_cold')
    drink_type = request.form.get('drink_type')
    drink_size = request.form.get('drink_size')

    drinks = coffee_data.Drinks()
    # Get the corresponding data from the Drinks class
    if hot_cold == 'Hot':
        data = drinks.hot_drinks.get(drink_type)
    elif hot_cold == 'Cold':
        data = drinks.cold_drinks.get(drink_type)
    else:
        data = None

    if data is not None:
        # Determine the index for the selected drink size
        if drink_size == 'Short':
            index = 0
        elif drink_size == 'Tall':
            index = 1
        elif drink_size == 'Grande':
            index = 2
        elif drink_size == 'Venti':
            index = 3
        elif drink_size == 'Trenta':
            index = 4
        else:
            index = -1  # Handle unknown sizes

        # Get the corresponding number
        number = data[index]

        if number != -1:
            session['counter'] += number

        return redirect(url_for('counter'))


