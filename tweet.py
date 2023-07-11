from os import environ
import tweepy
import gspread
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
import logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

#These keys are private to the user so it makes sense to keep them hidden, also good practice incase you want to deploy the web application on another website
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_TOKEN = environ['ACCESS_TOKEN']
ACCESS_SECRET = environ['ACCESS_SECRET']

#for Twitter API V2 if you go by the documentation it'll basically lead you down a rabbit hold of using OAuthentication which is incorrect
#Use tweepy.Client to easily authenticate without having to separately authenticate customer keys and access keys!
#Also make sure to set Access Keys to have read and write permission in order to be able to create tweets
client = tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)

#test
#client.create_tweet(text = 'Hi')

#getting google sheet so after tweet is tweeted we can assign done to 1 signifying completion and prompting a strike of the tweet
gc = gspread.service_account(filename='gsheet_credentials.json')

sh = gc.open_by_key('1uK8tMnkhxW3qd_EEopR5ZiiEYoJ27I70CZWfW5M7Abc')

worksheet = sh.sheet1

#setting debug = true and creating an interval to return when the tweet is tweeted and how many tweets are in the list 
INTERVAL = int(environ['INTERVAL']) 
DEBUG = environ['DEBUG'] == '1'

#function which locates the message, time, and if tweeted and then calculates the time to be tweeted and tweets the message if the time is reached
def main():
    while True:
        tweet_records = worksheet.get_all_records()
        current_time = datetime.utcnow() - timedelta(hours=5)
        #returning the number of tweets remaining to be tweeted
        logger.info(f'{len(tweet_records)} tweets found at at {current_time.time()}')
        for idx, tweet in enumerate(tweet_records, start=2):
            msg = tweet['message']
            time_str = tweet['time']
            done = tweet['done']
            #returning time obj in proper format
            date_time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            if not done:
                #converting time into current CT time
                now_time_ct = datetime.utcnow() - timedelta(hours=5)
                #if the time is properly formatted and in the future then tweet the message otherwise throw a warning
                if date_time_obj < now_time_ct:
                    logger.info('this should be tweeted')
                    try:
                        #updating the worksheet to reflect that the tweet has been tweeted
                        worksheet.update_cell(idx, 3, 1)
                        #this wouldn't normally work if using update_status()
                        client.create_tweet(text = msg)
                    except Exception as e:
                        logger.warning(f'exception during tweet! {e}')
        #running on set interval(60 seconds)
        time.sleep(INTERVAL)
if __name__ == '__main__':
    main()