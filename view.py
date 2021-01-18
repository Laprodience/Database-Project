from flask import Flask, render_template, current_app, abort, request, redirect, url_for, flash, session, escape
from object import User, Player, Team, Match, Bet
from datetime import datetime
from machine import insertMatch, executeMatch
import mysql.connector
from hashlib import sha256
import time

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
			session['nickname'] = user[0]
			return redirect(url_for('home_page'))
		else:
			msg = 'Incorrect username or password!'
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
			msg = 'Please fill the form!'
		else:
			hashedpw = create_hash(password)
			mycursor.execute('INSERT INTO users VALUES (%s, %s, %s, %s)', (nickname, hashedpw, 0, datetime.now().date(),))
			db.commit()
			return redirect(url_for('login_page'))
	elif request.method == 'POST':
		msg = 'Please fill the form!'
	return render_template('register.html', msg=msg)

def home_page():
	if 'loggedin' in session:
		return render_template('home.html')
	else:
		return redirect(url_for('login_page'))

def logout_page():
	session.pop('loggedin', None)
	session.pop('username', None)
	return redirect(url_for('login_page'))

def matches_page():
	if 'loggedin' in session:
		username = session['nickname']
		msg = ''
		returnid = int(0)
		today = datetime.now()
		pressed = 0
		upcoming = []
		ongoing = []
		played = []
		mycursor = db.cursor()
		mycursor.execute('SELECT id, team1, team2, team1_odd, team2_odd, date, score, winner FROM matches ORDER BY date ASC')
		for id, team1, team2, team1_odd, team2_odd, date, score, winner in mycursor:
			if(winner):
				played.append(Match(id, team1, team2, team1_odd, team2_odd, date, score, winner))
			else:
				if(today.strftime("%Y-%m-%d %H-%M") >= date):
					ongoing.append(Match(id, team1, team2, team1_odd, team2_odd, date, score, winner))
				else:
					upcoming.append(Match(id, team1, team2, team1_odd, team2_odd, date, score, winner))

		if request.method == 'POST' and 'betodd' in request.form and 'betamount' in request.form:
			betmatchid_odd = request.form['betodd']
			betmatchid_odd = str(betmatchid_odd)
			splitted = betmatchid_odd.split(", ")
			betmatchid = splitted[0]
			betmatchid = int(betmatchid)
			betmatchodd = splitted[1]
			betmatchodd = float(betmatchodd)
			betamount = request.form['betamount']
			betamount = float(betamount)

			mycursor5 = db.cursor()
			mycursor5.execute('SELECT balance FROM users WHERE nickname = %s', (username,))
			balance = mycursor5.fetchone()
			balance = str(balance)
			balance = balance.replace("'", " ")
			balance = balance.replace("(", " ")
			balance = balance.replace(")", " ")
			balance = balance.replace(",", " ")
			balance = float(balance)
			newbalance = balance - betamount

			if (betamount <= 0):
				returnid = betmatchid
				msg = 'You can only bet positive amounts!'

			if (newbalance < 0):
				returnid = betmatchid
				msg = "Your balance is not enough!"

			if(newbalance > 0) and (betamount > 0):
				mycursor5.execute('UPDATE users SET balance = %s WHERE nickname = %s', (newbalance, username,))
				mycursor4 = db.cursor()
				mycursor4.execute('SELECT id, team1, team2, team1_odd, team2_odd, date, score, winner FROM matches WHERE id = %s', (betmatchid,))
				id, team1, team2, team1_odd, team2_odd, date, score, winner = mycursor4.fetchone()
				if(betmatchodd == team1_odd):
					betteamname = team1
				elif(betmatchodd == team2_odd):
					betteamname = team2

				mycursor4.execute('INSERT INTO bets (user, team, matchid, amount, odd) VALUES (%s, %s, %s, %s, %s)', (username, betteamname, betmatchid, betamount, betmatchodd,))
				db.commit()
				
				return redirect(url_for('matches_page'))

		if request.method == 'POST' and request.form.get('startmatch'):
			scorewinner = []
			currentmatch = request.form.get('startmatch')

			mycursor2 = db.cursor()
			mycursor.execute('SELECT id, team1, team2, team1_odd, team2_odd, date, score, winner FROM matches WHERE id = %s', (currentmatch,))
			id, team1, team2, team1_odd, team2_odd, date, score, winner = mycursor2.fetchone()

			scorewinner = executeMatch(team1_odd, team2_odd)

			matchscore = scorewinner[0]
			if(scorewinner[1] == 1):
				winner = team1
			else:
				winner = team2

			mycursor3 = db.cursor()
			mycursor3.execute('UPDATE matches SET score = %s, winner = %s WHERE id = %s', (matchscore, winner, currentmatch,))
			db.commit()

			idholder = []
			userholder = []
			teamholder = []
			matchidholder = []
			amountholder = []
			oddholder = []

			mycursorx = db.cursor()
			mycursorx.execute('SELECT id, user, team, matchid, amount, odd FROM bets WHERE matchid = %s', (currentmatch,))
			for id, user, team, matchid, amount, odd in mycursorx:
				idholder.append(id)
				userholder.append(user)
				teamholder.append(team)
				matchidholder.append(matchid)
				amountholder.append(amount)
				oddholder.append(odd)

			i = 0
			for item in idholder:
				if (teamholder[i] == winner):
					mycursory = db.cursor()
					mycursory.execute('SELECT balance FROM users WHERE nickname = %s', (userholder[i],))
					balance = mycursory.fetchone()
					balance = str(balance)
					balance = balance.replace("'", " ")
					balance = balance.replace("(", " ")
					balance = balance.replace(")", " ")
					balance = balance.replace(",", " ")
					balance = float(balance)
					newbalance = balance + amount*odd
					mycursory.execute('UPDATE users SET balance = %s WHERE nickname = %s', (newbalance, userholder[i],))
					db.commit()
				mycursorz = db.cursor()
				mycursorz.execute('DELETE FROM bets WHERE id = %s', (idholder[i],))
				db.commit()
				i = i + 1

			return redirect(url_for('matches_page'))
			
		return render_template('matches.html', ongoing=ongoing, upcoming=upcoming, played=played, msg=msg, returnid=returnid)
	else:
		return redirect(url_for('login_page'))

def match_page():
	if 'loggedin' in session:
		return render_template('match.html')
	else:
		return redirect(url_for('login_page'))

def teams_page():
	if 'loggedin' in session:
		teams = []
		mycursor = db.cursor()
		mycursor.execute('SELECT name, teamrank, captain, sniper, entry_fragger, support, lurker FROM teams ORDER BY teamrank ASC')
		for name, teamrank, captain, sniper, entry_fragger, support, lurker in mycursor:
			teams.append(Team(name, teamrank, captain, sniper, entry_fragger, support, lurker))

		return render_template('teams.html', teams=teams)
	else:
		return redirect(url_for('login_page'))

def users_page():
	if 'loggedin' in session:
		users = []
		players = []
		searchresult = []

		mycursor4 = db.cursor()
		mycursor4.execute('SELECT COUNT(*) FROM players')
		playercount = str(mycursor4.fetchone())
		playercount = playercount.replace("'", " ")
		playercount = playercount.replace("(", " ")
		playercount = playercount.replace(")", " ")
		playercount = playercount.replace(",", " ")
		mycursor4.execute('SELECT COUNT(*) FROM users')
		usercount = str(mycursor4.fetchone())
		usercount = usercount.replace("'", " ")
		usercount = usercount.replace("(", " ")
		usercount = usercount.replace(")", " ")
		usercount = usercount.replace(",", " ")
		totalcount = int(playercount) + int(usercount)

		mycursor = db.cursor()
		mycursor.execute('SELECT nickname, rating, team, settings FROM players ORDER BY rating DESC')
		for nickname, rating, team, settings in mycursor:
			players.append(Player(nickname, rating, team, settings))

		mycursor2 = db.cursor()
		mycursor2.execute('SELECT nickname, balance, registerdate FROM users ORDER BY registerdate DESC')
		for nickname, balance, registerdate in mycursor2:
			users.append(User(nickname, balance, registerdate))

		if request.method == 'POST' and 'searchnm' in request.form:
			searchname = request.form['searchnm']
			mycursor3 = db.cursor()
			mycursor3.execute('SELECT nickname from users where nickname = %s UNION SELECT nickname from players where nickname = %s', (searchname, searchname,))
			for nickname in mycursor3:
				nickname = str(nickname)
				nickname = nickname.replace("'", " ")
				nickname = nickname.replace("(", " ")
				nickname = nickname.replace(")", " ")
				nickname = nickname.replace(",", " ")
				searchresult.append(nickname)

			if not searchresult:
				searchresult = ["User not found!"]

			return render_template('users.html', players=players, users=users,  searchresult=searchresult, playercount=playercount, usercount=usercount, totalcount=totalcount)

		return render_template('users.html', players=players, users=users,  searchresult=searchresult, playercount=playercount, usercount=usercount, totalcount=totalcount)
	else:
		return redirect(url_for('login_page'))

def top_page():
	if 'loggedin' in session:
		teams = []
		teams10 = []
		players = []
		players10 = []

		mycursor = db.cursor()
		mycursor.execute('SELECT nickname, rating, team, settings FROM players ORDER BY rating DESC')
		i = 0
		for nickname, rating, team, settings in mycursor:
			if i < 10:
				players10.append(Player(nickname, rating, team, settings))
			else:
				players.append(Player(nickname, rating, team, settings))
			i = i+1

		mycursor2 = db.cursor()
		mycursor2.execute('SELECT name, teamrank, captain, sniper, entry_fragger, support, lurker FROM teams ORDER BY teamrank ASC')
		i = 0
		for name, teamrank, captain, sniper, entry_fragger, support, lurker in mycursor2:
			if i < 10:
				teams10.append(Team(name, teamrank, captain, sniper, entry_fragger, support, lurker))
			else:
				teams.append(Team(name, teamrank, captain, sniper, entry_fragger, support, lurker))
			i = i+1

		return render_template('top.html', players10=players10, teams10=teams10)
	else:
		return redirect(url_for('login_page'))

def player_page(player_nickname):
	if 'loggedin' in session:
		mycursor = db.cursor()
		mycursor.execute('SELECT * FROM players WHERE nickname = %s', (player_nickname,))
		nickname, rating, team, settings = mycursor.fetchone()
		player = Player(nickname, rating, team, settings)
		imagen = player.nickname
		photostring = "images/" + imagen + ".webp"
		return render_template('player.html', player=player, player_nickname=player_nickname, photostring=photostring)
	else:
		return redirect(url_for('login_page'))

def profile_page():
	if 'loggedin' in session:
		msg = ''
		username = session['nickname']
		bets = []
		mycursor = db.cursor()
		mycursor.execute('SELECT nickname, balance, registerdate FROM users WHERE nickname = %s', (username,))
		nickname_, balance_, registerdate_ = mycursor.fetchone()
		user_ = User(nickname_, balance_, registerdate_)

		mycursor2 = db.cursor()
		mycursor2.execute('SELECT id, user, team, matchid, amount, odd FROM bets WHERE user = %s', (username,))
		for id, user, team, matchid, amount, odd in mycursor2:
				bets.append(Bet(id, user, team, matchid, amount, odd))

		if request.method == 'POST' and 'balance' in request.form:
			moneytoadd = request.form['balance']

			if float(moneytoadd) <= 0:
				msg = 'You can only add positive amounts!'

			else:
				newbalance = float(balance_) + float(moneytoadd)
				mycursor.execute('UPDATE users SET balance = %s WHERE nickname = %s', (newbalance, username,))
				db.commit()
				return redirect(url_for('profile_page'))

		elif request.method == 'POST' and 'pwupdate' in request.form:
			newpw = request.form['pwupdate']
			newpw = create_hash(newpw)
			mycursor.execute('UPDATE users SET password = %s WHERE nickname = %s', (newpw, username,))
			db.commit()
			return redirect(url_for('profile_page'))

		return render_template('profile.html', msg = msg, user_=user_, bets=bets)
	else:
		return redirect(url_for('login_page'))

def admin_page():
	if (session['nickname'] == "admin"):
		played = []
		mycursor3 = db.cursor()
		mycursor3.execute('SELECT id, team1, team2, team1_odd, team2_odd, date, score, winner FROM matches ORDER BY date ASC')
		for id, team1, team2, team1_odd, team2_odd, date, score, winner in mycursor3:
			if(winner):
				played.append(Match(id, team1, team2, team1_odd, team2_odd, date, score, winner))

		mycursor4 = db.cursor()
		if request.method == 'POST' and 'match_ids' in request.form:
			matches = request.form.getlist('match_ids')
			for matchid in matches:
				mycursor4.execute('DELETE FROM matches WHERE id = %s', (matchid,))
				db.commit()

			return redirect(url_for('admin_page'))

		elif request.method == 'POST' and 'team1' in request.form and 'team2' in request.form and 'date' in request.form:
			team1 = []
			team2 = []
			odds = []
			team1_ = request.form['team1']
			team2_ = request.form['team2']
			date_ = request.form['date']

			mycursor = db.cursor()
			mycursor.execute('SELECT nickname, rating, team, settings FROM players WHERE team = %s', (team1_,))
			for nickname, rating, team, settings in mycursor:
				team1.append(rating)
	
			mycursor2 = db.cursor()
			mycursor2.execute('SELECT nickname, rating, team, settings FROM players WHERE team = %s', (team2_,))
			for nickname, rating, team, settings in mycursor2:
				team2.append(rating)

			odds = insertMatch(team1, team2)
			score_ = "0 - 0"

			mycursor.execute('INSERT INTO matches (team1, team2, team1_odd, team2_odd, date, score) VALUES (%s, %s, %s, %s, %s, %s)', (team1_, team2_, odds[0], odds[1], date_, score_,))
			db.commit()

			return redirect(url_for('admin_page'))
		else:
			return render_template('adminpanel.html', played=played)
	else:
		return redirect(url_for('login_page'))