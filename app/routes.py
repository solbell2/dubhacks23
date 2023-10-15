from flask import render_template, session, redirect, url_for, request, flash
from app import app, coffee_data, db, firebase, auth

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
    if 'user' in session:
        return redirect(url_for('counter', user_id=session['user']))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(username, password)
            session['user'] = user['localId']
            return redirect(url_for('counter', user_id=user['localId']))
        except Exception as e:
            flash(f'Failed to login: {e}', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('homepage'))

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(username, password)
            session['user'] = user
            user_id = user['localId']
            return redirect(url_for('counter', user_id=user_id))
        except Exception as e:
            flash(f'Failed to register: {e}', 'error')

    return render_template('register.html')

# Define a route for counter
# Define a route for counter
@app.route('/counter/<string:user_id>')
def counter(user_id):
    hot_cold_options = ["Hot", "Cold"]
    drink_type_options = [
        "Americano", "Latte", "Flat white", "Cold brew", "Shaken espresso", 
        "Brewed coffee", "Brewed pike", "Brewed dark", "Chai", 
        "Black tea", "Green tea", "Passion tea", "Refresher", 
        "Frappuccino", "Creme Frappuccino"
    ]
    drink_size_options = ["Short", "Tall", "Grande", "Venti", "Trenta"]
    
    # Fetch user data from Firebase based on the user_id
    user_data = None
    try:
        user_data = firebase.database().child("users").child(user_id).get().val()
    except:
        flash('Failed to fetch user data', 'error')
    
    # Use a conditional statement to handle the case where user_data is None
    if user_data is not None:
        caffeine_count = user_data.get("caffeine", 0)
    else:
        caffeine_count = 0

    user = user_data
    
    return render_template('counter.html', user=user, user_id=user_id, counter=caffeine_count, hot_cold_options=hot_cold_options, drink_type_options=drink_type_options, drink_size_options=drink_size_options)

@app.route('/reset/<string:user_id>')
def reset(user_id):
    # Fetch user data from Firebase based on the user_id
    user_ref = firebase.database().child("users").child(user_id)
    user_data = user_ref.get().val()

    if user_data is not None:
        # Reset the caffeine counter to 0 and update it in the database
        user_data["caffeine"] = 0
        user_ref.set(user_data)
    else:
        flash('User not found', 'error')

    user = user_data

    return redirect(url_for('counter', user=user, user_id=user_id))

@app.route('/process/<string:user_id>', methods=['POST'])
def process(user_id):
    hot_cold = request.form.get('hot_cold')
    drink_type = request.form.get('drink_type')
    drink_size = request.form.get('drink_size')

    # Define your data for caffeine content
    caffeine_data = coffee_data.Drinks()

    # Get the corresponding data from the Drinks class
    if hot_cold == 'Hot':
        data = caffeine_data.hot_drinks.get(drink_type)
    elif hot_cold == 'Cold':
        data = caffeine_data.cold_drinks.get(drink_type)
    else:
        data = None

    # Fetch user data from Firebase based on the user_id
    user_ref = firebase.database().child("users").child(user_id)
    user_data = user_ref.get().val()

    if user_data is not None:
        # Determine the index for the selected drink size
        if data is not None:
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
            caffeine_intake = data[index]

            if caffeine_intake != -1:
                # Update the user's caffeine counter
                user_data["caffeine"] = user_data.get("caffeine", 0) + caffeine_intake
                user_ref.set(user_data)
        else:
            flash('Invalid drink type', 'error')
    else:
        flash('User not found', 'error')

    user = user_data

    return redirect(url_for('counter', user=user, user_id=user_id))

