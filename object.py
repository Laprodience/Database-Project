class User:
	def __init__ (self, nickname, balance, registerdate):
		self.nickname = nickname
		self.registerdate = registerdate
		self.balance = balance;

class Player:
	def __init__ (self, nickname, rating, team, settings):
		self.nickname = nickname
		self.rating = rating
		self.team = team
		self.settings = settings

class Team:
	def __init__ (self, name, teamrank, captain, sniper, entry_fragger, support, lurker):
		self.name = name
		self.teamrank = teamrank
		self.captain = captain
		self.sniper = sniper
		self.entry_fragger = entry_fragger
		self.support = support
		self.lurker = lurker

class Match:
	def __init__ (self, id, team1, team2, team1_odd, team2_odd, date, score, winner):
		self.id = id
		self.team1 = team1
		self.team2 = team2
		self.team1_odd = team1_odd
		self.team2_odd = team2_odd
		self.date = date
		self.score = score
		self.winner = winner

class Bet:
	def __init__ (self, id, user, team, matchid, amount, odd):
		self.id = id
		self.user = user
		self.team = team
		self.matchid = matchid
		self.amount = amount
		self.odd = odd