import os
import json
from dotenv import load_dotenv
from dictionary import get_dictionary
from sheet import str_to_sheet
from flask import Flask, request, jsonify, Response, send_file
from werkzeug.datastructures import FileStorage
from flask_cors import CORS
from models.base import Analysis
from models.reddit import RedditWrapper, RedditAnalyzer, Submission, Redditor
from models.twitter import TwitterData, TwitterStreamer, TwitterClient, TweetAnalyzer
from typing import List, IO
from tweepy import OAuthHandler
import tweepy
import praw
from translate import Translator

load_dotenv()

app = Flask(__name__)
translator= Translator(to_lang="Spanish")
CORS(app)
dictionary = get_dictionary(os.getenv("DICTIONARY_PATH"))
reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"), user_agent="my user agent", client_secret=os.getenv("REDDIT_CLIENT_SECRET"))
rwrapper = RedditWrapper(reddit, RedditAnalyzer(dictionary))

default_data = {
    "reddit" :{
        "users" : {},
        "subreddits": {}
    }
}

with open('./data/reddit.json', "r") as rfile:
    obj = json.load(rfile)
    default_data["reddit"]["users"] = obj["users"]
    default_data["reddit"]["subreddits"] = obj["subreddits"]

@app.route('/reddit/user', methods=["GET", "POST"])
def get_reddit_users():
    names: List[str] = []
    if request.method == "GET":
        return jsonify(default_data["reddit"]["users"])
    else:
        if 'plantilla' not in request.files:
            return Response("", status=400)
        else:
            data: FileStorage = request.files["plantilla"]
            sheet = str_to_sheet(data.stream.read())
            names = sheet["redditors_name"]
    users: List[dict] = []
    entries: int = 0
    for name in names:
        user_data = rwrapper.analyze_user_by_id(name)
        entries += user_data["n_entries"]
        users.append(user_data)
    return jsonify({
        "users":users,
        "n_entries":entries
    })

@app.route('/reddit/user/<id>', methods=["GET"])
def get_reddit_user(id: str):
    user_data = rwrapper.analyze_user_by_id(id)
    return jsonify({
        "user" : user_data
    })

@app.route('/reddit/subreddit', methods=["GET", "POST"])
def get_subreddits():
    names : List[str] = []
    if request.method == 'GET':
        return jsonify(default_data["reddit"]["subreddits"])
    else:
        if 'plantilla' not in request.files:
            return Response("", status=400)
        else:
            data: FileStorage = request.files['plantilla']
            sheet = str_to_sheet(data.stream.read())
            names = sheet["subreddits_name"]
    subreddits: List[Submission] = []
    entries: int = 0
    for name in names:
        subreddit_data = rwrapper.analyze_subreddit_by_id(name)
        entries += len(subreddit_data["submissions"])
        subreddits.append(subreddit_data)
    return jsonify({
        "subreddits": subreddits,
        "n_entries" : entries
    })

@app.route('/reddit/subreddit/<id>', methods=["GET"])
def get_subreddit(id: str):
    subreddit_data = rwrapper.analyze_subreddit_by_id(id)
    return jsonify({
        "subreddit" : subreddit_data
    })

@app.route("/reddit/analyze-sub", methods=["POST"])
def analyze_reddit_sub():
    data = request.json
    if "sub_id" in data:
        sub_id = data["sub_id"]
        if sub_id != "":
            analysis = rwrapper.analyze_submission_by_id(sub_id)
            return jsonify({"analysis" : analysis.toDict()})
    return Response("", status=400)


@app.route('/translate', methods=["POST"])
def translate_text():
    data = request.json
    text = data["text"]
    translation = translator.translate(text)
    return jsonify({"translation" : translation})

@app.route('/template', methods=["GET"])
def download():
    return send_file("../data/template.xlsx", as_attachment=True)

@app.route('/twitter/user', methods=["GET", "POST"])
def get_twitter_users():
    if request.method == "GET":
        names = ["ryanmdahl", "MagnusCarlsen", "denniskuo"]
    else:
        if 'plantilla' not in request.files:
            return Response("", status=400)
        else:
            data: FileStorage = request.files["plantilla"]
            sheet = str_to_sheet(data.stream.read())
            names = sheet["twitter_users"]
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    users = []
    entries = 0
    for name in names:
        user: tweepy.models.User = api.get_user(name)._json
        tweets: List[tweepy.models.Status] = api.user_timeline(user["id"])
        tws = []
        for tweet in tweets:
            tweet = tweet._json
            tw = {}
            tw["id"] = tweet["id"]
            tw["hashtags"] = [hashtag["text"] for hashtag in tweet["entities"]["hashtags"]]
            tw["retweet_count"] = tweet["retweet_count"]
            tw["text"] = tweet["text"]
            tws.append(tw)
        entries += len(tws)
        fmt_user = {
            "id" : user["id"],
            "name": user["name"],
            "description": user["description"],
            "location" : user["location"],
            "url" : user["url"],
            "verified" : user["verified"],
            "tweets_count": user["statuses_count"],
            "tweets": tws,
            "analysis": Analysis().toRandomDict()
        }
        users.append(fmt_user)
    return jsonify({"users" : users, "n_entries": entries})
    
@app.route('/twitter/user/<name>')
def get_twitter_user(name: str):
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    user: tweepy.models.User = api.get_user(name)._json
    tweets: List[tweepy.models.Status] = api.user_timeline(user["id"])
    tws = []
    for tweet in tweets:
        tweet = tweet._json
        tw = {}
        tw["id"] = tweet["id"]
        tw["hashtags"] = [hashtag["text"] for hashtag in tweet["entities"]["hashtags"]]
        tw["retweet_count"] = tweet["retweet_count"]
        tw["text"] = tweet["text"]
        tws.append(tw)
    fmt_user = {
        "id" : user["id"],
        "name": user["name"],
        "description": user["description"],
        "location" : user["location"],
        "url" : user["url"],
        "verified" : user["verified"],
        "tweets_count": user["statuses_count"],
        "tweets": tws,
        "analysis": Analysis().toRandomDict()
    }
    return jsonify({"user": fmt_user, "n_entries": len(tws)})

@app.route('/twitter/hashtags/<hashtag>')
def get_hashtag(hashtag: str):
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    tweets = tweepy.Cursor(api.search, q="#"+hashtag, rpp=10).items(limit=15)
    tws = []
    for tweet in tweets:
        tweet = tweet._json
        tw = {}
        tw["id"] = tweet["id"]
        tw["hashtags"] = [hashtag["text"] for hashtag in tweet["entities"]["hashtags"]]
        tw["retweet_count"] = tweet["retweet_count"]
        tw["text"] = tweet["text"]
        tws.append(tw)
    fmt_hashtag = {
        "name": "#" + hashtag,
        "tweets" : tws,
        "analysis" : Analysis().toRandomDict()
    }
    return jsonify({"hashtag" : fmt_hashtag, "n_entries" : len(tws)})

@app.route('/twitter/hashtags', methods=["GET", "POST"])
def get_hashtags():
    hashtag_names: List[str] = []
    if request.method == "GET":
        hashtag_names = ["#cats", "#dogs"]
    else:
        if 'plantilla' not in request.files:
            return Response("", status=400)
        else:
            data: FileStorage = request.files["plantilla"]
            sheet = str_to_sheet(data.stream.read())
            hashtag_names = sheet["hashtags"]
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    hashtags = []
    entries = 0
    for hashtag_name in hashtag_names:
        tweets = tweepy.Cursor(api.search, q=hashtag_name, rpp=10).items(limit=10)
        tws = []
        for tweet in tweets:
            tweet = tweet._json
            tw = {}
            tw["id"] = tweet["id"]
            tw["hashtags"] = [hashtag["text"] for hashtag in tweet["entities"]["hashtags"]]
            tw["retweet_count"] = tweet["retweet_count"]
            tw["text"] = tweet["text"]
            tws.append(tw)
        entries += len(tws)
        hashtags.append({"name" : hashtag_name, "tweets" : tws, "analysis": Analysis().toRandomDict()})
    return jsonify({"hashtags" : hashtags, "n_entries": entries})

if __name__ == "__main__":
    app.run("127.0.0.1", os.getenv("PORT"), debug=bool(os.getenv("DEBUG")))
