import os

from flask import Flask, session, render_template, request, url_for, flash, redirect, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from getApiData import getScoresToBeat, getWeeklyScores, getpointsfor, getallteamwins, getroster
import requests

app = Flask(__name__)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine('postgres://uppjytxixujjcg:ee4d0f848611a35592d0ace9b4af1e031ac7bae389394901079ff2086392beff@ec2-54-243-46-32.compute-1.amazonaws.com:5432/d2rkoq3jie1n31')
db = scoped_session(sessionmaker(bind=engine))
    
# set current season
current_season = 2019


# Get Current Week
week = db.execute("SELECT * FROM fffscores WHERE id = 1").fetchall()
current_week = -3
for column in week[0]:
    current_week += 1
    if column == 0:
        break

@app.route("/")
def home():
    # Query the database for data
    sortedbywin = db.execute("SELECT * FROM ffftable ORDER BY total_wins DESC, total_points DESC").fetchall()
    
    # Get Player with most points
    mostpf = db.execute("SELECT owner, total_points FROM ffftable ORDER BY total_points DESC").fetchone()
    
    # Get current places
    first = sortedbywin[0]
    second = sortedbywin[1]
    third = sortedbywin[2]

    # get header and welcome message
    welcome = db.execute("SELECT * FROM fff_welcome where id = 1").fetchall()


    # load top 100 players somehwere..
    #top100 = db.execute("SELECT * FROM fff100 ORDER BY playerrank")
    #print(top100)
    
    return render_template("home.html", sortedbywin=sortedbywin, first=first, second=second, third=third, mostpf = mostpf, current_week = current_week, welcome = welcome[0])

@app.route("/welcome", methods = ["GET", "POST"])
def welcome():
    # update welcome message to be displayed
    if request.method == "POST":
        header = request.form.get("title")
        message = request.form.get("message")

        db.execute("UPDATE fff_welcome SET title = :title, message = :message WHERE id = 1", {"title": header, "message": message})        
        db.commit()
        return redirect("/")

    elif request.method == "GET":
        return render_template("welcome.html")


@app.route("/playoffs")
def playoffs():
    # Query the database for data
    sortedbywin = db.execute("SELECT * FROM ffftable ORDER BY total_wins DESC, total_points DESC").fetchall()
    
    # Get Player with most points
    mostpf = db.execute("SELECT owner, total_points FROM ffftable ORDER BY total_points DESC").fetchone()
    
    # Get current places
    first = sortedbywin[0]
    second = sortedbywin[1]
    third = sortedbywin[2]
    
    return render_template("playoffs.html", sortedbywin=sortedbywin, first=first, second=second, third=third, mostpf = mostpf, current_week = current_week)

@app.route("/<int:view_week>")
def homeextra(view_week):

    if view_week < 0 or view_week > 17:
        return render_template("error.html", error="invalid url")

    # Query the database for data
    sortedbywin = db.execute("SELECT * FROM ffftable ORDER BY total_wins DESC, total_points DESC").fetchall()
    
    # Get Player with most points
    mostpf = db.execute("SELECT owner, total_points FROM ffftable ORDER BY total_points DESC").fetchone()

    # get header and welcome message
    welcome = db.execute("SELECT * FROM fff_welcome where id = 1").fetchall()
    
    if view_week != 0 and view_week < 17 and view_week > 0:
        some_week = db.execute("SELECT * FROM fffscores").fetchall()
        
        # make a sorted list of tuples (owner, score)
        week_scores = []
        index = view_week + 1
        
        # get owner, score for the given week
        for owner in some_week:
            score = owner[index]
            owner = owner.team_name
            week_scores.append((score, owner))

        # send week number and sorted (score : owner) to data table
        week_scores.sort(key=lambda tup: tup[0], reverse=True) 
        week = view_week

        # Get total score of week.
        score_counter = 0
        for scores in some_week:
            score_counter += scores[index]
        
    
    else:
        some_week is None

    
    return render_template("home.html", sortedbywin=sortedbywin, mostpf = mostpf, some_week=some_week, week_scores=week_scores, week=week, current_week = current_week, score_counter=score_counter, welcome = welcome[0])

@app.route("/<string:sort_by>")
def sorted(sort_by):
    
    # Query the database for data, depending on url
    if sort_by == "total_points" or sort_by == "average_score":
        sortedby = db.execute("SELECT * FROM ffftable ORDER BY total_points DESC").fetchall()
    
    elif sort_by == "h2h":
        sortedby = db.execute("SELECT * FROM ffftable ORDER BY wins DESC, total_points DESC").fetchall()
    
    elif sort_by == "top6":
        sortedby = db.execute("SELECT * FROM ffftable ORDER BY top6 DESC, total_points DESC").fetchall()
    
    else:
        sortedby = db.execute("SELECT * FROM ffftable ORDER BY total_wins DESC, total_points DESC").fetchall()

    # Get Player with most points
    mostpf = db.execute("SELECT owner, total_points FROM ffftable ORDER BY total_points DESC").fetchone()
    
    # Get current places
    first = sortedby[0]
    second = sortedby[1]
    third = sortedby[2]


    return render_template("home.html", sortedbywin=sortedby, first=first, second=second, third=third, mostpf = mostpf, current_week = current_week)

@app.route("/data")
def data():
    
    rosters = db.execute("SELECT * FROM fffrosters ORDER BY id").fetchall()
    q = db.execute("SELECT * FROM fff100 ORDER BY playerrank").fetchall()

    # convert fff100 players into interesting lists
    top100list = []
    top12rblist = []
    top12wrlist = []
    for z in range(0, 100):
        top100list.append(q[z][1])
        if q[z][2] == "WR":
            top12wrlist.append(q[z][1])
        if q[z][2] == "RB":
            top12rblist.append(q[z][1])

    top12rblist = top12rblist[:12]
    top12wrlist = top12wrlist[:12]

    # Create Lists and Counters
    top100counter = 0
    listofcounters = []
    top12rbcounter = 0
    listofrbcounters = []
    top12wrcounter = 0
    listofwrcounters = []

    # Iterate through lists and increase counts
    for row in rosters:
        for eachcolumn in row:
            if isinstance(row, int):
                continue
            if eachcolumn in top100list:
                top100counter+=1
            if eachcolumn in top12wrlist:
                top12wrcounter +=1
            if eachcolumn in top12rblist:
                top12rbcounter +=1

        
        # Add to lists (in order of player id) the number of players they have
        listofcounters.append(top100counter)
        listofrbcounters.append(top12rbcounter)
        listofwrcounters.append(top12wrcounter)
        # Reset counters for next player
        top100counter = 0
        top12wrcounter = 0
        top12rbcounter = 0
    
    
    return render_template("graph.html", numberoftop100 = listofcounters, top12wr = listofwrcounters, top12rb = listofrbcounters)


@app.route("/player/<int:id>")
def player(id):
    '''display an owners roster, player draft price, and keeper price'''

    if id < 1 or id > 12:
        return render_template("error.html", error="That page doesn't exist.")

    getteamname = db.execute("SELECT id, owner FROM ffftable ORDER BY id")
    for player in getteamname:
        if id == player.id:
            owner = player.owner
            break
    
    data = getroster(id)
    roster = data[1]
    currentseason = data[0]

    return render_template("player1.html", datalist = roster, owner = owner, currentseason = currentseason)

@app.route("/update", methods=["GET"])
def update():
    '''update number of h2h wins, top6 wins and total wins'''
    '''Don't refresh after games have started'''
        
    # Get List of all pf, already ordered by owner id
    pf_list = getpointsfor()
    
    # get scoretobeat (STB) from espnff
    scoretobeat = getScoresToBeat() # else use this: scoretobeat = [105.1, 112.4, 107.2, 108.5, 107.5, 103.8, 109.3, 112.3, 103.5, 0, 0, 0, 0]

    # get weekly scoring data from table
    data = db.execute("SELECT * FROM ffftable ORDER BY id").fetchall()

    # Get list of all team wins
    team = getallteamwins()
    m=0 # index for list of players
    
    # Loop through each player in data table, and reset index/counter
    for player in data:
        counter=0 # times each player surpasses STB
        n=6 # index of db for weekly scoring
        
        
        # Calculate number of weeks in top6 scoring
        for week in range(1,14):

            # Stop counting if player score is 0 or STB is 0
            if player[n] == "0" or scoretobeat[week-1] == 0:
                break
            
            # If a player doesn't surpass STB, break
            if float(player[n]) > scoretobeat[week-1]:
                counter += 1

            #move to next week in index
            n += 1
        
        wintotal = team[m].wins + counter
        db.execute("UPDATE ffftable SET wins = :wins, top6 = :top6, total_wins = :total_wins, total_points = :pf WHERE id=:id", 
                    {"wins": team[m].wins, "top6": counter, "total_wins": wintotal, "pf": pf_list[m], "id": player.id })
        db.commit()
        print(player.owner + ": ", end='')
        print(team[m].wins, end='')
        print(" H2H wins, ", end='')
        print(counter, end='') 
        print(" top6 apperances and ", end='')
        print(wintotal, end='')
        print(" total wins!")
        
        m+=1 # advance index to next list item

    return render_template("update.html")
                    
@app.route("/weeklyupdate", methods=["GET", "POST"])
def weeklyupdate():
    '''udpate db with scores from the week'''
    '''in week 10, be sure the UPDATE to the scores table is the correct data type'''

    if request.method == "POST":
        if not request.form.get("week"):
            return render_template("home.html")
        else:
        
            week = int(request.form.get("week"))
            scoreDict = getWeeklyScores(week)
            for n in range(0, 12):
                id = n+1
                singlescore = str(scoreDict[n])
                floatscore = float(scoreDict[n])
                
                # Update scores in both tables, given the week
                if week == 9:
                    db.execute("UPDATE ffftable SET scores_wk9 = :score WHERE id = :id", {"score": singlescore, "id": id})
                elif week == 10:
                    db.execute("UPDATE ffftable SET scores_wk10 = :score WHERE id = :id", {"score": singlescore, "id": id})
                    db.execute("UPDATE fffscores SET wk10_scores = :score WHERE id = :id", {"score": floatscore, "id": id})
                elif week == 11:
                    db.execute("UPDATE ffftable SET scores_wk11 = :score WHERE id = :id", {"score": singlescore, "id": id})
                    db.execute("UPDATE fffscores SET wk11_scores = :score WHERE id = :id", {"score": floatscore, "id": id})
                elif week == 12:
                    db.execute("UPDATE ffftable SET scores_wk12 = :score WHERE id = :id", {"score": singlescore, "id": id})
                    db.execute("UPDATE fffscores SET wk12_scores = :score WHERE id = :id", {"score": floatscore, "id": id})
                elif week == 13:
                    db.execute("UPDATE ffftable SET scores_wk13 = :score WHERE id = :id", {"score": singlescore, "id": id})
                    db.execute("UPDATE fffscores SET wk13_scores = :score WHERE id = :id", {"score": floatscore, "id": id})
                elif week == 14:
                    db.execute("UPDATE ffftable SET scores_wk14 = :score WHERE id = :id", {"score": singlescore, "id": id})
                    db.execute("UPDATE fffscores SET wk14_scores = :score WHERE id = :id", {"score": floatscore, "id": id})
                elif week == 15:
                    db.execute("UPDATE ffftable SET scores_wk15 = :score WHERE id = :id", {"score": singlescore, "id": id})
                    db.execute("UPDATE fffscores SET wk15_scores = :score WHERE id = :id", {"score": floatscore, "id": id})
                elif week == 16:
                    db.execute("UPDATE ffftable SET scores_wk16 = :score WHERE id = :id", {"score": singlescore, "id": id})
                    db.execute("UPDATE fffscores SET wk16_scores = :score WHERE id = :id", {"score": floatscore, "id": id})
                else:
                    return render_template("home.html")
            db.commit()

            return render_template("weeklyupdate.html")
    
    else:
        return render_template("weeklyupdate.html")