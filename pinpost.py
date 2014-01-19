# Muhan Zhang
# MHacks 2014
# Built on Michelle's design, implemented registration to entry.

# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our application
# app = Flask(__name__)

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
	cur = g.db.execute('select users, pws from entries order by id desc')
	entries = [dict(user=row[0], pws=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries=entries)




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

# original login method without database integration
# @app.route('/login', methods=['GET', 'POST'])
# def login():
# 	error = None
# 	if request.method == 'POST':
# 		if request.form['username'] != app.config['USERNAME']:
# 			error = 'Invalid username'
# 		elif request.form['password'] != app.config['PASSWORD']:
# 			error = 'Invalid password'
# 		else:
# 			session['logged_in'] = True
# 			flash('You were logged in')
# 			return redirect(url_for('show_entries'))
# 	return render_template('login.html', error=error)

#based off of the login and new post
@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		render_template('register.html')

		# print 'post'
		# g.db.execute('insert into entries (users, pws) values (?, ?)', 
		# 		 [request.form['un'], request.form['pw']])

		# artifacts from when we were taking input and putting it into entries as strings
		# g.db.execute('insert into entries (users, pws) values (?, ?)', 
		# 		 [request.form['un'], "password: " + request.form['pw'] + \
		# 		 					", pinterest handle: " + request.form['ph'] + \
		# 		 					", street address: " + request.form['st'] + \
		# 		 					", city, state, zip: " + request.form['zp']])

		# # flash('User: ' + request.form['un'])
		# g.db.commit()

		# flash ('User: ' + request.form['un'])

#name, pinterest handle, username, password, email, address
		# Session = sessionmaker()
		# session = Session()
	
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

		# cur = g.db.execute('select users, pws from entries order by id desc')
		# 	entries = [dict(user=row[0], pws=row[1]) for row in cur.fetchall()]
		# 	return render_template('show_entries.html', entries=entries)

	#return redirect(url_for('register'))

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))
	
if __name__ == '__main__':
	app.run()