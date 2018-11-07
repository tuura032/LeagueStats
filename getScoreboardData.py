# https://github.com/rbarton65/espnff

from espnff import League
league_id = 877873
year = 2018
league = League(league_id, year)
league.scoreboard() # grab current week
scoreboard_main = league.scoreboard(week=1) # define week

def getscorestobeat():
    '''Get Score to Beat for weeks 1-13'''
    allscorestobeat = []

    for week in range(1, 14):
        scoreboard = league.scoreboard(week=week)
        tempstorage = []
        for matchups in scoreboard:
            tempstorage.append(matchups.home_score)
            tempstorage.append(matchups.away_score)
        tempstorage.sort()
        allscorestobeat.append(tempstorage[5])

    return allscorestobeat

def getweekscores(week_num):
    '''Get All Scores from a given week in a list'''

    week_index = int(week_num) - 1
    week_scores = [] # empty list for all scores
    
    for player in range(0, 12):
        team = league.teams[player]
        week_scores.append(team.scores[week_index])

    return week_scores

def getpointsfor():
    '''update points_for'''

    pf_list = []
    # update points_for for all 12 owners
    for n in range(0, 12):
        team = league.teams[n]
        pf_list.append(team.points_for)

    return pf_list
        


def getallownerscores(ownerID):
    '''Get All Scores From a Single Owner'''

    ownerID -= 1
    team = league.teams[ownerID]
    allownerscores = team.scores
    teamname = team.team_name
    print(teamname)

    return allownerscores

def getallteamwins():
    '''Return a list of h2h wins'''
    team = league.teams

    return team