from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager 
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////mnt/c/Users/antho/Documents/twitter_clone/engage.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'ksdlfkdsofidsithnaljnfadksjhfdskjfbnjewrhewuirhfsenfdsjkfhdksjhfdslfjasldkj'

configure_uploads(app, photos)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(30))
    image = db.Column(db.String(100))
    password = db.Column(db.String(50))

class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('A full name is required.'), Length(max=100, message='Your name can\'t be more than 100 characters.')])
    username = StringField('Username', validators=[InputRequired('Username is required.'), Length(max=30, message='Your username is too many characters.')])
    password = PasswordField('Password', validators=[InputRequired('A password is required.')])
    image = FileField(validators=[FileAllowed(IMAGES, 'Only images are accepted.')])

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    remember = BooleanField('Remember me')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if form.validate_on_submit():
        return '<h1>Username: {}, Password: {}, Remember: {}</h1>'.format(form.username.data, form.password.data, form.remember.data)

    return render_template('index.html', form=form)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        image_filename = photos.save(form.image.data)
        image_url = photos.url(image_filename)

        new_user = User(name=form.name.data, username=form.username.data, image=image_url, password=generate_password_hash(form.password.data))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('profile'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    manager.run()