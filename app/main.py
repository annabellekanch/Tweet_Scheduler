from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import gspread

app = Flask(__name__)

#getting the email assigned by googlesheets api
gc = gspread.service_account(filename='gsheet_credentials.json')

#getting the google sheet and setting worksheet value to sheet 1
sh = gc.open_by_key('1uK8tMnkhxW3qd_EEopR5ZiiEYoJ27I70CZWfW5M7Abc')

worksheet = sh.sheet1

#class to store message, time, if the tweet has been tweeted, and row index
class Tweet:
    def __init__(self, message, time, done, row_idx):
        self.message = message
        self.time = time
        self.done = done
        self.row_idx = row_idx
        
#this function will get the convert the time to a proper unit and then check to see if the time given by the user is in the past
def get_date_time(date_time_str):
    date_time_obj = None
    error_code = None
    #if user gives time input in any other format throw an error
    try:
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        error_code = f'Error! {e}'
    
    #if time is not empty then convert time to the time currently
    #if time currently is less then time given then throw an error
    if date_time_obj is not None:
        now_time_ct = datetime.utcnow() - timedelta(hours=5)
        if not date_time_obj > now_time_ct:
            error_code = "error! time must be in the future"
    return date_time_obj, error_code    

#creating tweet list and assigning each tweet a 0 or 1 based on if they were tweeted yet       
@app.route("/")
def tweet_list():
    tweet_records = worksheet.get_all_records()
    tweets = []
    for idx, tweet in enumerate(tweet_records, start=2):
        tweet = Tweet(**tweet, row_idx=idx)
        tweets.append(tweet)
    tweets.reverse()
    n_open_tweets = sum(1 for tweet in tweets if not tweet.done)
    return render_template('base.html', tweets=tweets, n_open_tweets=n_open_tweets)

#getting input from form for tweet message, tweet time, and tweet password & throwing error if otherwise
@app.route("/tweet", methods=['POST'])
def add_tweet():
    message = request.form['message']
    if not message:
        return "error! no message"
    time = request.form['time']
    if not time:
        return "error! no time"
    password = request.form['pw']
    if not password or password != "something123":
        return "error! wrong password"
    
    if len(message) > 280:
        return "error! message too long"
    
    date_time_obj, error_code = get_date_time(time)
    if error_code is not None:
        return error_code
    #if tweet is properly formatted then add the tweet to the worksheet & list and redirect back to creating a tweet
    tweet = [str(date_time_obj), message, 0]
    worksheet.append_row(tweet)
    return redirect('/')

#function to delete any tweets scheduled or already tweeted with a delete button
@app.route("/delete/<int:row_idx>")
def delete_tweet(row_idx):
    worksheet.delete_rows(row_idx)
    return redirect('/')