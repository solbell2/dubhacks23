from flask import render_template, session, redirect, url_for, request, flash
from flask_login import login_user, login_required, login_manager, logout_user
from app import app, coffee_data, db, User, UserDrinks
from datetime import datetime

# Define a route for the homepage
@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

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
            return redirect(url_for('counter', user_id=user.id))
        else:
            flash('Login failed. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

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

@app.route('/counter/<int:user_id>')
@login_required
def counter(user_id):
    # Fetch the user based on user_id
    user = User.query.get(user_id)

    if user is not None:
        hot_cold_options = ["Hot", "Cold"]
        drink_type_options = [
            "Americano", "Latte", "Flat white", "Cold brew", "Shaken espresso", 
            "Brewed coffee", "Brewed pike", "Brewed dark", "Chai", 
            "Black tea", "Green tea", "Passion tea", "Refresher", 
            "Frappuccino", "Creme Frappuccino"
        ]
        drink_size_options = ["Short", "Tall", "Grande", "Venti", "Trenta"]
        
        # Query the user's recent drinks
        recent_drinks = user.drinks[-10:]  # Get the last 10 drinks

        return render_template('counter.html', user=user, user_id=user.id, counter=user.caffeine, hot_cold_options=hot_cold_options, drink_type_options=drink_type_options, drink_size_options=drink_size_options, recent_drinks=recent_drinks)
    else:
        flash('User not found', 'error')
        return redirect(url_for('homepage'))


@app.route('/reset/<int:user_id>')
@login_required
def reset(user_id):
    user = User.query.get(user_id)
    user.caffeine = 0
    db.session.commit()
    return redirect(url_for('counter', user_id=user.id))

@app.route('/process/<int:user_id>', methods=['POST'])
@login_required
def process(user_id):
    user = User.query.get(user_id)
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
            # Log the drink
            new_drink = UserDrinks(user_id=user_id, drink_type=drink_type, drink_size=drink_size, timestamp=datetime.now())
            db.session.add(new_drink)

            # Update user caffeine counter
            user.caffeine += number
            db.session.commit()

        return redirect(url_for('counter', user_id=user.id))


