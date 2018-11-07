# TODO I'm struggling with the varchar values of scores_wk_. I might need to just create a new data table (which is fine), or not deal with sorting scores. 
# also STB udpates only through week 9, I should have it go until it reaches a null value. maybe a while loop instead? Or just add an if statement and break.

import os

from flask import Flask, session, render_template, request, url_for, flash, redirect, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from getScoreboardData import getscorestobeat, getweekscores, getpointsfor, getallteamwins
import requests
from espnff import League

app = Flask(__name__)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine('postgres://uppjytxixujjcg:ee4d0f848611a35592d0ace9b4af1e031ac7bae389394901079ff2086392beff@ec2-54-243-46-32.compute-1.amazonaws.com:5432/d2rkoq3jie1n31')
db = scoped_session(sessionmaker(bind=engine))


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
    
    
    return render_template("home.html", sortedbywin=sortedbywin, first=first, second=second, third=third, mostpf = mostpf)

@app.route("/<int:view_week>")
def homeextra(view_week):
    # Query the database for data
    sortedbywin = db.execute("SELECT * FROM ffftable ORDER BY total_wins DESC, total_points DESC").fetchall()
    
    # Get Player with most points
    mostpf = db.execute("SELECT owner, total_points FROM ffftable ORDER BY total_points DESC").fetchone()
    
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
    
    else:
        some_week is None
    
    
    return render_template("home.html", sortedbywin=sortedbywin, mostpf = mostpf, some_week=some_week, week_scores=week_scores, week=week)

@app.route("/update", methods=["GET"])
def update():
    '''update number of h2h wins, top6 wins and total wins'''
    '''Don't refresh after games have started'''
        
    # Get List of all pf, already ordered by owner id
    pf_list = getpointsfor()
    
    # get scoretobeat (STB) from espnff
    scoretobeat = getscorestobeat() # else use this: scoretobeat = [105.1, 112.4, 107.2, 108.5, 107.5, 103.8, 109.3, 112.3, 103.5, 0, 0, 0, 0]

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
            listofscores = getweekscores(week)
            for n in range(0, 12):
                id = n+1
                singlescore = str(listofscores[n])
                floatscore = float(listofscores[n])
                
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