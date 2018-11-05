import os

from flask import Flask, session, render_template, request, url_for, flash, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from getScoreboardData import getscorestobeat
import requests

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
    everything = db.execute("SELECT * FROM ffftable").fetchall()
    sortedbywin = db.execute("SELECT * FROM ffftable ORDER BY total_wins DESC").fetchall()
    
    # Figure out who has the most points
    
    sortpf = db.execute("SELECT owner, points_for FROM ffftable WHERE LENGTH(points_for) > 5 ORDER BY points_for DESC").fetchall()
    
    

    first = sortedbywin[0]
    second = sortedbywin[1]
    third = sortedbywin[2]
    mostpf = sortpf[0]

    
    return render_template("home.html", everything=everything, sortedbywin=sortedbywin, first=first, second=second, third=third, mostpf = mostpf)


    #orm examples
    #ffftable.query.all()
    #ffftable.query.filter_by(colulmn_name = 'something').all() // or .first()

@app.route("/update", methods=["GET", "POST"])
def update():

    #if request.method == "POST":
        #update number of top6 wins
        #scoretobeat = getscorestobeat()
        scoretobeat = [105.1, 112.4, 107.2, 108.5, 107.5, 103.8, 109.3, 112.3, 0, 0, 0, 0]
        #scores = 'scores_wk'+str(n)
        data = db.execute("SELECT * FROM ffftable").fetchall()
        
        # Loop through each player, and reset variables
        for player in data:
            counter=0
            n=6 # index of db for weekly scoring
            
            # Increase counter each week a player surpasses STB
            for week in range(1,10):
                
                # If a player doesn't surpass STB, break
                if float(player[n]) > scoretobeat[week-1]:
                    if scoretobeat[week-1] == 0:
                        break
                    #db.execute("UPDATE top6 SET top6 = :top6", {"top6": +=1})
                    counter += 1
                    #print(player.owner + ": ", end='')
                    #print(player[n]) #print score from each week
                    #print("Beat score of: ", end='')
                    #print(scoretobeat[week-1])
                    #print("Top 6 wins: ", end='')
                    #print(counter)
                n += 1
            
            wintotal = player.wins + counter
            db.execute("UPDATE ffftable SET top6 = :top6, total_wins = :total_wins WHERE id=:id", {"top6": counter, "total_wins": wintotal, "id": player.id })
            db.commit()
            print(player.owner + ": ", end='')
            print(counter, end='') 
            print(" top6 apperances and ", end='')
            print(wintotal, end='')
            print(" total wins!")

        return render_template("update.html")
                    
