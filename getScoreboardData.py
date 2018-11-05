# https://github.com/rbarton65/espnff

from espnff import League
league_id = 877873
year = 2018
league = League(league_id, year)
league.scoreboard() # grab current week
scoreboard_main = league.scoreboard(week=1) # define week

def getscorestobeat():
    allscorestobeat = []

    for week in range(1, 13):
        scoreboard = league.scoreboard(week=week)
        tempstorage = []
        for matchups in scoreboard:
            tempstorage.append(matchups.home_score)
            tempstorage.append(matchups.away_score)
        tempstorage.sort()
        allscorestobeat.append(tempstorage[5])

    return allscorestobeat

#x = getscorestobeat()
#print(x)