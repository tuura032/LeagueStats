# get data from espn api v3
import requests

league_id = 877873
year = 2018


def getScoresToBeat():
    '''Get Score to Beat for weeks 1-13'''
    # probably done
    
    # make request
    mteam = requests.get('http://fantasy.espn.com/apis/v3/games/ffl/seasons/2018/segments/0/leagues/877873?view=mMatchupScore')
    myjson = mteam.json()
    
    allscorestobeat = []

    for week in range(1, 14):
        week_index = (int(week) - 1) * 6
        tempstorage = []
        for matchup in range(week_index, (week_index + 6)):
            tempstorage.append(myjson['schedule'][matchup]['home']['totalPoints'])
            tempstorage.append(myjson['schedule'][matchup]['away']['totalPoints'])
        tempstorage.sort()
        
        # after sorting, 5th index is STB
        allscorestobeat.append(tempstorage[5])

    return allscorestobeat

def getWeeklyScores(week):
    '''Get All Scores from a given week in a list'''
    # probably done

    mteam = requests.get('http://fantasy.espn.com/apis/v3/games/ffl/seasons/2018/segments/0/leagues/877873?view=mMatchupScore')
    myjson = mteam.json()

    week_index = (int(week) - 1) * 6
    week_scores = {} # empty dict for all scores

    for matchup in range((week_index), (week_index + 6)):
        week_scores[myjson['schedule'][matchup]['home']['teamId']] = myjson['schedule'][0]['home']['totalPoints']
        week_scores[myjson['schedule'][matchup]['home']['teamId']] = myjson['schedule'][0]['home']['totalPoints']

    return week_scores

def getpointsfor():
    #done updating
    '''update points_for'''
    
    mteam = requests.get('http://fantasy.espn.com/apis/v3/games/ffl/seasons/2018/segments/0/leagues/877873?view=mTeam')
    myjson = mteam.json()
    pf_list = []

    # update points_for for all 12 owners
    for player_index in range(0, 12):
        
        pf_list.append(myjson['teams'][player_index]['record']['overall']['pointsFor'])

    return pf_list

def getallteamwins():
    '''returns dict of  {player_id : wins} of each player'''
    # make sure to fix application.py to work with dict, not list of teams
    mteam = requests.get('http://fantasy.espn.com/apis/v3/games/ffl/seasons/2018/segments/0/leagues/877873?view=mTeam')
    myjson = mteam.json()
    
    teams = {}
    
    for player_index in range(0-11):
        teams[myjson['teams'][player_index]['id']] = myjson['teams'][player_index]['record']['overall']['wins']

    return teams

def getroster(id):
    # done
    '''taking in owner id, return current roster'''
    
    # get json data
    r = requests.get('http://fantasy.espn.com/apis/v3/games/ffl/seasons/2018/segments/0/leagues/877873?view=mRoster')
    myjson = r.json()

    # Get at data from each player
    datalist = []
    owner_index = id -1
    for player_index in range(0, 15):
        fullname = myjson['teams'][owner_index]['roster']['entries'][player_index]['playerPoolEntry']['player']['fullName']
        auctionvalue = myjson['teams'][owner_index]['roster']['entries'][player_index]['playerPoolEntry']['keeperValueFuture'] + 7
        #playerdata = (1, firstname+" "+ lastname, auctionvalue)
        
        # Set Keeper Price
        keeperprice = auctionvalue + 7
        if auctionvalue == 0:
            keeperprice = 12
        if fullname == "Todd Gurley II" or fullname == "Alvin Kamara" or fullname == "Keenan Allen" or fullname == "Zach Ertz" or fullname == "Tyreek Hill" or fullname == "Davante Adams" or fullname == "Adam Thielen" or \
                    fullname == "Derek Henry" or fullname == "Russell Wilson" or fullname == "Ezekiel Elliot" or fullname == "Lamar Miller" or fullname == "JuJu Smith-Schuster" or fullname == "Marvin Jones Jr" or \
                    fullname == "Marquis Goodwin" or fullname == "Jamaal Williams":
            keeperprice += 3
        if fullname == "Melvin Gordon" or fullname == "Michael Thomas":
            keeperprice = "n/a"
        text = f'{fullname} is on your roster and was drafted for ${auctionvalue} and can be kept for ${keeperprice}'
        datalist.append(text)

    return datalist

