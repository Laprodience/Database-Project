import random
import time
import math


def insertMatch(team1, team2):
	output = []
	team1sum = (team1[0] * team1[1] * team1[2] * team1[3] * team1[4])
	team2sum = (team2[0] * team2[1] * team2[2] * team2[3] * team2[4])
	totalsum = team1sum + team2sum
	team1prob = team1sum / totalsum
	team2prob = team2sum / totalsum
	equalprob = int(math.factorial(30)/(math.factorial(15)*math.factorial(15)))*(pow(team1prob, 15))*(pow(team2prob, 15))

	margin = 0.05
	team1odd = 1 / (team1prob + margin)
	team2odd = 1 / (team2prob + margin)
	if team1odd <= 1.00:
		team1odd = 1.01
	if team2odd <= 1.00:
		team2odd = 1.01
	
	team1odd = round(team1odd, 2)
	team2odd = round(team2odd, 2)
	output.append(team1odd)
	output.append(team2odd)

	return output

def executeMatch(team1odd, team2odd):
	output = []
	team1prob = (1 / team1odd) - 0.05
	team2prob = (1 / team2odd) - 0.05
	team1counter = 0
	team2counter = 0
	roundcounter = 0
	overtimecounter = 0
	overtimerepeat = 1

	while(roundcounter<30 and (team1counter < 16 and team2counter < 16)):
		roundoutcome = random.uniform(0, 1)
		if(roundoutcome < team1prob):
			team1counter = team1counter + 1
		else:
			team2counter = team2counter + 1

		roundcounter = roundcounter + 1
	
		if(roundcounter == 30 and team1counter == team2counter):
			while(overtimecounter < 6 and (team1counter < (16 + overtimerepeat*3) and team2counter < (16 + overtimerepeat*3))):
				roundoutcome = random.uniform(0, 1)
				if(roundoutcome < team1prob):
					team1counter = team1counter + 1
				else:
					team2counter = team2counter + 1

				overtimecounter = overtimecounter + 1
				if(overtimecounter == 6 and team1counter == team2counter):
					overtimecounter = 0
					overtimerepeat = overtimerepeat + 1


	score = str(team1counter)
	score = score + " - "
	score = score + str(team2counter)
	output.append(score)
	if(team1counter > team2counter):
		winner = 1

	else:
		winner = 2

	output.append(winner)
	return output