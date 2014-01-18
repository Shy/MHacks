# Muhan Zhang
# MHacks 2014
# Built on Michelle's design, implemented registration to entry.

# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our application
app = Flask(__name__)
app.config.from_object(__name__)

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
		user = query_db('select * from users where username = ?',
		                request.form['username'], one=True)
		if user is None:
		    print 'No such user'
		else:
		    print the_username, 'has the id', user['user_id']

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

		g.db.execute('insert into entries (users, pws) values (?, ?)', 
				 [request.form['un'], request.form['pw']])

		# artifacts from when we were taking input and putting it into entries as strings
		# g.db.execute('insert into entries (users, pws) values (?, ?)', 
		# 		 [request.form['un'], "password: " + request.form['pw'] + \
		# 		 					", pinterest handle: " + request.form['ph'] + \
		# 		 					", street address: " + request.form['st'] + \
		# 		 					", city, state, zip: " + request.form['zp']])

		# flash('User: ' + request.form['un'])
		g.db.commit()

		flash ('User: ' + request.form['un'])

		# cur = g.db.execute('select users, pws from entries order by id desc')
		# 	entries = [dict(user=row[0], pws=row[1]) for row in cur.fetchall()]
		# 	return render_template('show_entries.html', entries=entries)

		return redirect(url_for('show_entries'))

	return render_template('register.html')

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))
	
if __name__ == '__main__':
	app.run()