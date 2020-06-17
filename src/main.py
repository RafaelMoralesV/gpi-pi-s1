from dictionary import get_dictionary
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from models.base import Analysis
from models.reddit import RedditWrapper, RedditAnalyzer
from models.twitter import TwitterData, TwitterStreamer, TwitterClient, TweetAnalyzer
from tweepy import OAuthHandler
import tweepy
import praw
from translate import Translator

app = Flask(__name__)
translator= Translator(to_lang="Spanish")
CORS(app)
dictionary = get_dictionary('./data/diccionario.json')
reddit = praw.Reddit(client_id="AUs7RM1sxg8Itg", user_agent="my user agent", client_secret="NVkkQtixo7aMWnDjGqi8fCmUP_g")
rwrapper = RedditWrapper(reddit, RedditAnalyzer(dictionary))

@app.route('/reddit/user/<id>', methods=["GET"])
def get_reddit_user(id: str):
    user = rwrapper.reddit.redditor(id)
    analysis = Analysis().toRandomDict()
    return jsonify({
        "user" : {
            "analysis" : analysis,
            "icon_img" : user.icon_img,
            "id" : user.id,
            "name" : user.name,
        }
    })

@app.route('/reddit/subreddit', methods=["GET"])
def get_subreddits():
    subreddits = []
    names = ["golang", "Fitness", "lectures", "videogames", "politics", "Paranormal"]
    for name in names:
        subreddit = rwrapper.reddit.subreddit(name)
        analysis = Analysis().toRandomDict()
        subreddits.append({
            "analysis" : analysis,
            "description": subreddit.public_description,
            "id" : subreddit.id,
            "name": subreddit.display_name,
            "subscribers" : subreddit.subscribers,
            "over18" : subreddit.over18
        })
    
    return jsonify({
        "subreddits": subreddits,
        "n_entries" : 230
    })

@app.route('/reddit/subreddit/<id>', methods=["GET"])
def get_subreddit(id: str):
    subreddit = rwrapper.reddit.subreddit(id)
    
    analysis = Analysis().toRandomDict()

    subs = []
    for sub in subreddit.hot(limit=25):
        subs.append({
            "id" : sub.id,
            "name": sub.title,
            "n_comments" : sub.num_comments,
            "text" : sub.selftext
        })
    
    return jsonify({
        "subreddit" : {
            "analysis" : analysis,
            "description": subreddit.public_description,
            "id" : subreddit.id,
            "name": subreddit.display_name,
            "subscribers" : subreddit.subscribers,
            "over18" : subreddit.over18
        },
        "n_entries" : 25,
        "submissions" : subs
    })

@app.route('/translate', methods=["POST"])
def translate_text():
    data = request.json
    text = data["text"]
    translation = translator.translate(text)
    return jsonify({"translation" : translation})

@app.route('/twitter/user/<name>')
def get_twitter_user(name: str):
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    user = api.get_user(name)
    return jsonify({"user": user._json})

@app.route('/twitter')
def get_tweet():
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    user = api.get_user("MagnusCarlsen")
    tweets = api.user_timeline(user.id)
    tweet : tweepy.models.Status = tweets[0]
    #tws = [tweet for tweet in tweets]
    #for tw in tws:
    #    print(tw.text)
    #replies = tweepy.Cursor(api.search, q=f"to:{'MagnusCarlsen'}", since_id=tws[2].id, tweet_mode="extended").items()
    #for reply in replies:
    #    pass
    return jsonify({"msg" : tweet._json})

if __name__ == "__main__":
    app.run("127.0.0.1", "5000", debug=True)