from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for storing user information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(100), nullable=True)
    links = db.Column(db.Text, nullable=True)

# Model for storing contact form submissions
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)


# Route for the homepage
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create-portfolio', methods=['GET', 'POST'])
def create_portfolio():
    if request.method == 'POST':
        # Collect form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        bio = request.form['bio']
        skills = request.form['skills']
        links = request.form['links']

        # Handle profile picture upload
        profile_picture = request.files['profile_picture']
        profile_pic_filename = None
        if profile_picture:
            profile_pic_filename = profile_picture.filename
            profile_picture.save(os.path.join('static', profile_pic_filename))

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Email already exists, redirect with a message or error
            return render_template('form.html', error="This email is already in use. Please use another email.")

        # Create a new User object and save to the database
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            bio=bio,
            skills=skills,
            profile_picture=profile_pic_filename,
            links=links
        )
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the thank you page after submission
        return redirect(url_for('thankyou'))

    return render_template('form.html')

# Route for the portfolio page, showing the latest user data
@app.route('/portfolio/<int:user_id>')
def portfolio(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('portfolio.html', user=user)

# Route for the "Thank You" page, showing the latest submitted portfolio
@app.route('/thankyou')
def thankyou():
    # Get the last submitted user data
    user = User.query.order_by(User.id.desc()).first()
    return render_template('thankyou.html', user=user)

# Custom third page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Collect form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Save the data to the database
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()

        # Redirect to the thank you page after submission
        return redirect(url_for('contact_thankyou'))

    return render_template('custom.html')


if __name__ == '__main__':
    # Ensure the database and tables are created within the app context
    with app.app_context():
        db.create_all()  # Create tables inside the app context
    app.run(debug=True)
