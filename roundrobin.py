#!Py3.x
import csv
import math
import random
import re

random.seed()
#n round chess odds estimator for single round-robin
#Monte Carlo analysis, since tournament endings will change based on prize dynamics
f = open ("GCT2017.txt")
seedRatingName = dict()
for line in f.readlines():
    splitline = line.split()
    seedRatingName[splitline[0]] = splitline[1:]
drawdiff = dict()
with open ("idiotexcel.csv") as csvfile: #This file has draw rates from chess-db.com
    reader = csv.reader(csvfile)
    for row in reader:
        try:
            drawdiff[int(row.pop(0))] = row
        except:
            continue
        #assign row[0] to a key in drawdiff with values row[1] to row[n]
pairings = dict() #global
def loadBerger(players): #Returns the round pairings as per FIDE handbook
    players = players + players % 2
    foundLine = 0
    i = 1
    berger = open("bergertables.txt")
    strPlayers = str(players) + " p" #searches for the paragraph start
    s = []
    for line in berger.readlines():
        if line.find(strPlayers) != -1:
            foundLine = 1
        if 0 < foundLine <= players:
            if foundLine != 1:
                s.append(line)
            foundLine = foundLine + 1
    s = ''.join(s)
    for line in s.split('\n'):
        pairings[i] = re.findall("[0-9]+\-[0-9]+",line)
        i = i + 1
    return(pairings)

def drawcalc(elowhite,eloblack):
    hi = max(elowhite,eloblack)
    low = min(elowhite,eloblack)
    diffac = ((hi - low) % 20)/20
    difcol = int(math.floor((hi - low) / 20)) #should give us the list item
    #interpolate or extrapolate
    if hi > 2600:
        factor = (hi - low)/(2600 - low)
        x200 = 2600 #since there is no 2800 row we have to interpolate this way
        drawatfloor = (float(drawdiff[x200][difcol + 1]) - float(drawdiff[x200][difcol])) * diffac + float(drawdiff[x200][difcol])
        drawat2600 = (float(drawdiff[2600][difcol + 1]) - float(drawdiff[2600][difcol])) * diffac + float(drawdiff[2600][difcol])
        drawodds = drawatfloor + (drawat2600 - drawatfloor) * factor
    else:
        factor = (hi % 200)/200 #the factor to multiply by within rows separated by 200 Elo
        x200 = int(math.floor(hi/200)*200)
        drawatfloor = (float(drawdiff[x200][difcol + 1]) - float(drawdiff[x200][difcol])) * diffac + float(drawdiff[x200][difcol])
        drawatceil = (float(drawdiff[x200 + 200][difcol + 1]) - float(drawdiff[x200 + 200][difcol])) * diffac + float(drawdiff[x200 + 200][difcol])
        drawodds = drawatfloor + (drawatceil - drawatfloor) * factor
    #x200 tells us which row (key) to use
    return(drawodds)

def elopredict(elowhite,eloblack):
    drawchance = drawcalc(elowhite,eloblack)
    elowhite = elowhite + 17.5 * flip
    eloblack = eloblack - 17.5 * flip
    ex1w = 1/(1+10**((elowhite-eloblack)/400)) #Elo's formula for winning chances
    w2l = ex1w/(1-ex1w)
    # use draw rate from https://chess-db.com/public/research/draw_rate.html
    # interpolate to find draw rate
    # Jeff Sonas - White adv = 35Elo, therefore add 17.5 to white and subtract 17.5 from black
    ex1l = (1-drawchance)*(w2l/(w2l+1)) #chance of white losing outright after draws are considered
    ex1w = 1 - drawchance - ex1l #chance of white winning
    return([ex1w,drawchance,ex1l])

#elopredict(int(d[p1]),int(d[p2]))

def randOutcome(wdl):
    outcome = random.random()
    if wdl[0] > outcome:
        return (2.000000001) #we return this instead of 2 because of the tiebreak rules favoring number of wins.
    if wdl[0] <= outcome < (wdl[0]+wdl[1]):
        return (1)
    if (wdl[0]+wdl[1]) < outcome:
        return (0)

def makePairs(n):
    n = n % 2 + n
    i = 1
    wins = [0]*n
    for j in range(n): #j is a dummy variable
        for pair in pairings[i]:
            wb = pair.split("-") #wb[0] and wb[1] are the seednumber of white and black
            outcome = randOutcome(elopredict(float(seedRatingName[wb[0]][0]),float(seedRatingName[wb[1]][0])))
            #make crosstable based on outcome. Could probably cleverly cut this time in half.
            crosstable[int(wb[0])-1][int(wb[1])-1] = math.floor(outcome)
            crosstable[int(wb[1])-1][int(wb[0])-1] = 2 - math.floor(outcome)
            wins[int(wb[0])-1] = wins[int(wb[0])-1] + outcome 
            wins[int(wb[1])-1] = wins[int(wb[1])-1] + 2 - outcome 
        i = i + 1
    return(wins)
    
def tieBreak(winners): #will only do the head-to-head tiebreak, as the "most wins" tiebreak is covered by elopredict()
    winner = winners[0]
    for playerElement in winners:
        crosstable[playerElement][playerElement] = 0
        for i in range(n):
            if i in winners:
                crosstable[playerElement][i] = 0
        if sum(crosstable[playerElement]) > sum(crosstable[winner]):
            winner = playerElement #slight bug here. Technically we should go to rapid/blitz tiebreaks but since it's less than 1% of the time this is negligible
    return(winner)

def flipCoin(): #hacky way to reverse white/black pairings 50% of the time
    if random.random() < 0.5:
        return (1)
    else:
        return (-1)

n = 10
counts = 10000
points = [0]*n
wincount = [0]*n
loadBerger(n)
for count in range(counts): #running the sim for all counts
    flip = flipCoin()
    crosstable = [[[] for i in range(n)] for j in range(n)] #initializing
    wins = makePairs(n) #list of wins for each player, in order
    m = max(wins)
    winners = [i for i,j in enumerate(wins) if j == m] #gives us all player elements with max wins
    if len(winners) > 1:
        winners = tieBreak(winners) #only run tiebreaks if there is a tie.
    else:
        winners = winners[0]
    for i in range(n):
        if i == winners:
            wincount[i] = wincount[i] + 1 #probably a clever dictionary way to do this.
    points = [points[i]+wins[i] for i in range(n)] #adding totals across Monte Carlo
winpercent = [100*wincount[i]/counts for i in range(n)] #win percent, per player element
print(winpercent) #win percent of each player
for i in range(n):
    player = str(i+1)
    print(seedRatingName[player][1], "Implied odds:", round((100-winpercent[i])/winpercent[i],2), ":1")

#MIT License. Please credit Michael Loo or BrainForecast.com