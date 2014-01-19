# Muhan Zhang
# MHacks 2014
# Built on Michelle's design, implemented registration to entry.

# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
import lob
import Pinterest_Socket
import Lob_Socket
from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired


# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
lob.api_key = 'test_0bead6806b12c3668ee03810cf181c78141'


app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True)
	pinterest_handle = db.Column(db.String(80), unique=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80), unique=False)
	email = db.Column(db.String(120), unique=True)
	address_line1 = db.Column(db.String(150), unique=False)
	address_line2 = db.Column(db.String(150), unique=False)
	address_city = db.Column(db.String(150), unique=False)
	address_state = db.Column(db.String(150), unique=False)
	address_zip = db.Column(db.String(150), unique=False)

	def __init__(self, name, pinterest_handle, username, password, email, address_line1, address_line2, 
		address_city, address_state, address_zip):
		self.name = name
		self.pinterest_handle = pinterest_handle
		self.username = username
		self.password = password
		self.email = email
		self.address_line1 = address_line1
		self.address_line2 = address_line2
		self.address_city = address_city
		self.address_state = address_state
		self.address_zip = address_zip

	def __repr__(self):
		return '<User %r>' % self.username

#db.drop_all()
#db.create_all()

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

# new stuff from flash sqlite3 documentation
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
def show_entries():
	return render_template('show_entries.html', entries=[])

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	g.db.execute('insert into entries (title, text) values (?, ?)', 
				 [request.form['title'], request.form['text']])
	g.db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

# attempting to convert user login system to a database
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		user_login = request.form['username']
		print user_login
		user = User.query.filter_by(username=user_login).first()
		print user
		#user = query_db('select * from users where username = ?',
		#                request.form['username'], one=True)
		if user is None:
		    print 'No such user'
		else:
			passwd = request.form['password']
			if passwd == user.password:
				print 'Login Successful'
				#flash('Login Successful')
			else:
				print 'incorrect password'
		    #print the_username, 'has the id', user['user_id']

	else:
		print 'what'
		# session['logged_in'] = True
		# flash('You were logged in')
		# return redirect(url_for('show_entries'))

	return render_template('login.html', error=error)

#based off of the login and new post
@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		render_template('register.html')
	
		name = request.form['name']
		pinterest = request.form['ph']
		username = request.form['un']
		password = request.form['pw']
		email = request.form['email']
		line1 = request.form['st1']
		line2 = request.form['st2']
		city = request.form['city']
		state = request.form['state']
		addr_zip = request.form['zp']

		newUser = User(name=name, pinterest_handle=pinterest, username=username, password=password, email=email, 
			address_line1=line1, address_line2=line2, address_city=city, address_state=state, address_zip=addr_zip)
		print newUser.name
		db.session.add(newUser)
		db.session.commit()
		users = User.query.all()
		print users
		flash('Congratulations ' + newUser.name)
	return render_template('register.html')

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

@app.route('/admin_send_postcards')
def admin_send_postcards():
	lob.api_key = 'test_0bead6806b12c3668ee03810cf181c78141'
	for u in db.session.query(User):
		print u.name
	#TODO: render a proper view
	return render_template('login.html')

class CardForm(Form):
	pinterest_name = TextField('Pinterest Name', validators=[DataRequired()])
	address_name = TextField('Name', validators=[DataRequired()])
	address_email = TextField('Email', validators=[DataRequired()])
	address_line1 = TextField('Address Line 1', validators=[DataRequired()])
	address_line2 = TextField('Address Line 2', validators=[])
	address_city = TextField('City', validators=[DataRequired()])
	address_state = TextField('State', validators=[DataRequired()])
	address_zip = TextField('Zip', validators=[DataRequired()])


@app.route('/card', methods=['GET', 'POST'])
def card():
	form = CardForm()
	if request.method == 'POST' and form.validate():
		try:
			top_pin = Pinterest_Socket.Get(form.pinterest_name.data)
		except Exception, e:
			#TOOD: show pinterest error
			print "Pinterest error occurred"
			return render_template('card.html', form=form)

		message = ""
		if top_pin["description"] and top_pin["domain"]:
			message = top_pin["description"] + "\n- " + top_pin["domain"]
		elif top_pin["description"]:
			message = top_pin["description"]
		elif top_pin["domain"]:
			message = top_pin["domain"]

		toaddr = lob.Address.create(
			name=form.address_name.data,
			address_line1=form.address_line1.data,
			address_line2=form.address_line2.data,
			email=form.address_email.data,
			address_city=form.address_city.data,
			address_state=form.address_state.data,
			address_country="US",
			address_zip=form.address_zip.data).to_dict()

		try:
			Lob_Socket.SendPostcard(top_pin['image_large_url'], toaddr, message)
		except Exception, e:
			#TODO: show lob error
			print "Lob error occurred"
			return render_template('card.html', form=form)
		return redirect(url_for('card'))
	else:
		#TODO: show vailidation errors in card.html
		return render_template('card.html', form=form)


	
if __name__ == '__main__':
	app.run()