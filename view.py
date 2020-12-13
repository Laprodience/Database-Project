from flask import Flask, render_template, current_app, abort, request, redirect, url_for, flash, session, escape
from object import User
from datetime import datetime
import mysql.connector
from hashlib import sha256

def create_hash(password):
	pw_bytestring = password.encode()
	return sha256(pw_bytestring).hexdigest()

db = mysql.connector.connect(
	host="localhost",
	user="root",
	password="Drakula66",
	database="counterbet"
) 

def login_page():
	msg = ''
	if request.method == 'POST' and 'nickname' in request.form and 'password' in request.form:
		nickname = request.form['nickname']
		password = request.form['password']
		mycursor = db.cursor()
		hashedpw = create_hash(password)
		mycursor.execute('SELECT * FROM users WHERE nickname = %s AND password = %s', (nickname, hashedpw,))
		user = mycursor.fetchone()
		if user:
			session['loggedin'] = True
			session['id'] = user[0]
			session['nickname'] = user[1]
			return redirect(url_for('home_page'))
		else:
			msg = 'Incorrect username/password!'
	return render_template('login.html', msg=msg)

def register_page():
	msg = ''
	if request.method == 'POST' and 'nickname' in request.form and 'password' in request.form:
		nickname = request.form['nickname']
		password = request.form['password']
		mycursor = db.cursor()
		mycursor.execute('SELECT * FROM users WHERE nickname = %s', (nickname,))
		user = mycursor.fetchone()
		if user:
			msg = 'Account already exists!'
		elif not nickname or not password:
			msg = 'Please fill out the form!'
		else:
			hashedpw = create_hash(password)
			mycursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (nickname, hashedpw, 0, datetime.now().date(),))
			db.commit()
			return redirect(url_for('home_page'))
	elif request.method == 'POST':
		msg = 'Please fill out the form!'
	return render_template('register.html', msg=msg)

def home_page():
	if 'loggedin' in session:
		return render_template('home.html', nickname=session['nickname'])
	return redirect(url_for('login_page'))

def logout_page():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login_page'))