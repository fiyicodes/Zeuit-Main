import os

from flask import Flask, jsonify, redirect, render_template, url_for, request
from twitter import TwitterClient
import praw
import tweepy
from analysis import subredditAnalysis, userTweetAnalysis, searchTweetAnalysis, customTextAnalysis

# Configure application
app = Flask(__name__)

# Setup the client <query string, retweets_only bool, with_sentiment bool>
api = TwitterClient('@codedatt')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# To avoid caching of static files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Render routes

@app.route('/')
def index():
    return (render_template("index.html"))

@app.route('/reddit')
def reddit():
    return render_template("reddit-main.html")

#@app.route('/twitter')
#def twitter():
#    return render_template("twitter.html")

#@app.route('/instagram')
#def instagram():
#    return render_template("instagram.html")

def strtobool(v):
    return v.lower() in ["yes", "true", "t", "1"]


@app.route('/twitter')
def twittertest():

    return render_template('twitter-test.html')


@app.route('/tweets')
def tweets():
        retweets_only = request.args.get('retweets_only')
        api.set_retweet_checking(strtobool(retweets_only.lower()))
        with_sentiment = request.args.get('with_sentiment')
        api.set_with_sentiment(strtobool(with_sentiment.lower()))
        query = request.args.get('query')
        api.set_query(query)

        tweets = api.get_tweets()
        return jsonify({'data': tweets, 'count': len(tweets)})

    ####
@app.route('/custom')
def custom():
    return render_template("custom-main.html")

@app.route('/analyse')
def analyse(template):
    return render_template(template)  

# Validation routes
@app.route('/redditValidate')
def redditValidate():
    # Connect with Reddit API
    reddit = praw.Reddit(client_id = "F7wsA_lS5CIW_g", 
                     client_secret = "TTqI5XAZk_ev3gQ4bPOwwQIAaVA", 
                     user_agent = "subSentiment")

    subreddit = request.args.get("subreddit")
    sub_exists = True

    try:
        reddit.subreddits.search_by_name(subreddit, exact=True)
    except:
        sub_exists = False

    if sub_exists and len(subreddit) > 0: 
        return jsonify(exists='T')
    else:
        return jsonify(exists='F')

@app.route('/twitterValidate')
def twitterValidate():
    # Connecting to Twitter API through Tweepy
    consumer_key = "UPujFYkbzD9oJpyCoM6XU2vPi"
    consumer_secret = "Ffl8IsEOi8TaPRp6kVVEwoLoL4hCRvlCHKCnXtrCAyzyUmsxOL"
    access_token = "1707276163-dEAZhIChOSwl8GlAjF0E4MwiWEvbSv5rMbLzN93"
    access_token_secret = "QSUI3rEFF4NocP7vMDF5IjpU2FXhCSBlpkTDFkdZtOAYt"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    valid = True

    if request.args.get("key") == 'user':
        try:
            api.get_user(screen_name=request.args.get("value"))
        except:
            valid = False
    else:
        try:
            tweets = tweepy.Cursor(api.search, q="#"+request.args.get("value")).items(1)
        except:
            valid = False

    if valid:
        return jsonify(exists='T')
    else:
        return jsonify(exists='F')

# Analysis routes
@app.route('/redditAnalyse')
def redditAnalyse():
    subreddit = request.args.get("subreddit")
    timeframe = request.args.get("timeframe")  

    polarity, subjectivity = subredditAnalysis(subreddit, timeframe)

    return jsonify(polarity=polarity, subjectivity=subjectivity)

@app.route('/twitterAnalyse')
def twitterAnalyse():
    if request.args.get("key") == 'user':
        polarity, subjectivity = userTweetAnalysis(request.args.get("value"), int(request.args.get("count")))
    else:
        polarity, subjectivity = searchTweetAnalysis(request.args.get("value"), int(request.args.get("count")))

    return jsonify(polarity=polarity, subjectivity=subjectivity)

@app.route('/customTextAnalyse')
def customTextAnalyse():
    polarity, subjectivity = customTextAnalysis(request.args.get("text"))

    return jsonify(polarity=polarity, subjectivity=subjectivity)

port = int(os.environ.get('PORT', 5000))
app.run(host="0.0.0.0", port=port, debug=True)
        