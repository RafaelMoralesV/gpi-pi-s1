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
from models.twitter import TwitterData, TwitterStreamer, TwitterClient, TwitterAnalyzer
from typing import List, IO
from tweepy import OAuthHandler
import tweepy
import praw
from statistics import mean
from translate import Translator

load_dotenv()

app = Flask(__name__)
translator= Translator(to_lang="Spanish")
CORS(app)
dictionary = get_dictionary(os.getenv("DICTIONARY_PATH"))
reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"), user_agent="my user agent", client_secret=os.getenv("REDDIT_CLIENT_SECRET"))
rwrapper = RedditWrapper(reddit, RedditAnalyzer(dictionary))
twitter_client = TwitterClient()
twitter_analyzer = TwitterAnalyzer(dictionary)

default_data = {
    "reddit" :{
        "users" : {},
        "subreddits": {}
    },
    "twitter": {
        "users":{},
        "hashtags": {}
    }
}

with open('./data/reddit.json', "r") as rfile:
    obj = json.load(rfile)
    default_data["reddit"]["users"] = obj["users"]
    default_data["reddit"]["subreddits"] = obj["subreddits"]

with open('./data/twitter.json', "r") as tfile:
    obj = json.load(tfile)
    default_data["twitter"]["users"] = obj["users"]
    default_data["twitter"]["hashtags"] = obj["hashtags"]

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
            if len(names) == 0:
                return Response("Columna Vacía", status=422)
    users: List[dict] = []
    entries: int = 0
    for name in names:
        user_data = rwrapper.analyze_user_by_id(name)
        entries += user_data["n_entries"]
        users.append(user_data)
    analysis = dict()
    for key in list(users[0]["analysis"].keys()):
        analysis[key] = mean([user_data["analysis"][key] for user_data in users])

    return jsonify({
        "analysis": analysis,
        "users":users,
        "n_entries":entries
    })

@app.route('/reddit/user/<id>', methods=["GET"])
def get_reddit_user(id: str):
    user_data = rwrapper.analyze_user_by_id(id)
    return jsonify({
        "analysis": user_data["analysis"],
        "user" : user_data,
        "n_entries" : user_data["n_entries"]
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
            if len(names) == 0:
                return Response("Columna Vacía", status=422)
    subreddits: List[dict] = []
    entries: int = 0
    for name in names:
        subreddit_data = rwrapper.analyze_subreddit_by_id(name)
        entries += len(subreddit_data["submissions"])
        subreddits.append(subreddit_data)
    analysis = dict()
    for key in list(subreddits[0]["analysis"].keys()):
        analysis[key] = mean([subreddit_data["analysis"][key] for subreddit_data in subreddits])
    return jsonify({
        "analysis" : analysis,
        "subreddits": subreddits,
        "n_entries" : entries
    })

@app.route('/reddit/subreddit/<id>', methods=["GET"])
def get_subreddit(id: str):
    subreddit_data = rwrapper.analyze_subreddit_by_id(id)
    return jsonify({
        "analysis": subreddit_data["analysis"],
        "subreddit" : subreddit_data,
        "n_entries": subreddit_data["n_entries"]
    })

@app.route("/reddit/analyze-sub", methods=["POST"])
def analyze_reddit_sub():
    data = request.json
    if "sub_id" in data:
        sub_id = data["sub_id"]
        if sub_id != "":
            try:
                analysis = rwrapper.analyze_submission_by_id(sub_id)
                return jsonify({"analysis" : analysis.toDict()})
            except Exception as err:
                return Response("Registro no encontrado", status=404)
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

@app.route('/twitter/hashtags/<hashtag>')
def get_twitter_hashtag(hashtag: str):
    analysis = twitter_analyzer.analyze_by_hashtag(hashtag,twitter_client)
    return jsonify({
        "analysis": analysis[1].toDict(),
        "name": hashtag,
        "tweets": analysis[0],
        "n_entries": len(analysis[0])
    })

@app.route('/twitter/user/<name>')
def get_tweets(name: str):
    user = twitter_client.twitter_client.get_user(name)._json
    analysis = twitter_analyzer.analyze_user_by_name(name,twitter_client)
    user["tweets"] = analysis[0]
    user["analysis"] = analysis[1].toDict()
    user["n_entries"] = len(analysis[0])
    return jsonify(user)

@app.route('/twitter/analyze-tweet', methods=["POST"])
def get_tweet():
    data = request.json
    if "tweet_id" in data: 
        tweet_id = data["tweet_id"]
        tweets_ids = [tweet_id]
        text_tweets = []
        try:
            text_tweets = twitter_client.get_tweet_to_analyze(tweets_ids)
        except Exception as err:
            return Response("Registro no encontrado", status=404)
        autoconciencia_emocional = twitter_analyzer.get_autoconciencia_by_group(text_tweets)
        autoestima = twitter_analyzer.get_autoestima_by_group(text_tweets)
        comprension_organizativa = twitter_analyzer.get_comprension_by_group(text_tweets)
        comunicacion_asertiva = twitter_analyzer.get_comunicacion_asertiva_by_group(text_tweets)
        conciencia_critica = twitter_analyzer.get_conciencia_critica_by_group(text_tweets)
        motivacion_de_logro = twitter_analyzer.get_motivacion_by_group(text_tweets,'usuario')
        tolerancia = twitter_analyzer.get_tolerancia_by_group(text_tweets, 'usuario')
        desarrollar_y_estimular_a_los_demas = twitter_analyzer.get_desarrollar_by_group_user(text_tweets)
        empatia = twitter_analyzer.get_empatia_by_group_user(text_tweets)
        colaboracion_cooperacion = twitter_analyzer.get_collaboration_cooperation_by_group(text_tweets, 'user')
        percepcion_comprension_emocional = twitter_analyzer.get_percepcion_comprension_emocional_by_group(text_tweets, 'user')
        liderazgo = twitter_analyzer.get_liderazgo_by_group_user(text_tweets)
        manejo_de_conflictos = twitter_analyzer.get_manejo_de_conflictos_by_group(text_tweets, 'user')
        violencia = twitter_analyzer.get_violencia_by_group(text_tweets, 'user')
        relacion_social = twitter_analyzer.get_relacion_social_by_group(text_tweets, 'user')
        optimismo = twitter_analyzer.get_optimismo_by_group(text_tweets, 'user')
        analysis = Analysis(
            autoconciencia_emocional=autoconciencia_emocional,autoestima=autoestima,
            comprension_organizativa=comprension_organizativa, asertividad=comunicacion_asertiva,
            conciencia_critica=conciencia_critica,motivacion_logro=motivacion_de_logro,
            tolerancia_frustracion=tolerancia,desarrollar_estimular=desarrollar_y_estimular_a_los_demas,
            empatia=empatia, colaboracion_cooperacion=colaboracion_cooperacion, percepcion_comprension_emocional=percepcion_comprension_emocional,
            manejo_conflictos=manejo_de_conflictos, violencia=violencia, relacion_social=relacion_social, optimismo=optimismo,liderazgo = liderazgo)

        return jsonify({
            "analysis" : analysis.toDict()
        })
    return Response("", status=400)

@app.route('/twitter/user', methods=["GET","POST"])
def get_twitter_users():
    if request.method == "GET":
        return jsonify(default_data["twitter"]["users"])
    else:
        if 'plantilla' not in request.files:
            return Response("", status=400)
        else:
            data: FileStorage = request.files["plantilla"]
            sheet = str_to_sheet(data.stream.read())
            names = sheet["twitter_users"]
            if len(names) == 0:
                return Response("Columna Vacía", status=422)
    users: List[dict] = []
    entries: int = 0
    for name in names:
        user = twitter_client.twitter_client.get_user(name)._json
        analysis = twitter_analyzer.analyze_user_by_name(name,twitter_client)
        user["analysis"] = analysis[1].toDict()
        user["tweets"] = analysis[0]
        user_data = user
        user_data["analysis"] = analysis[1].toDict()
        user_data["n_entries"] = len(analysis[0])
        entries += user_data["n_entries"]
        users.append(user_data)
    analysis = dict()
    for key in list(users[0]["analysis"].keys()):
        analysis[key] = mean([user_data["analysis"][key] for user_data in users])
    return jsonify({
        "analysis" : analysis,
        "users":users,
        "n_entries":entries
    })

@app.route('/twitter/hashtags', methods=["GET","POST"])
def get_twitter_hashtags():
    if request.method == "GET":
        return jsonify(default_data["twitter"]["hashtags"])
    else:
        if 'plantilla' not in request.files:
            return Response("", status=400)
        else:
            data: FileStorage = request.files["plantilla"]
            sheet = str_to_sheet(data.stream.read())
            hashtags = sheet["hashtags"]
            if len(hashtags) == 0:
                return Response("Columna Vacía", status=422)
    hashtag_list: List[dict] = []
    entries: int = 0
    for hashtag in hashtags:
        analysis = twitter_analyzer.analyze_by_hashtag(hashtag,twitter_client)
        hashtag_data = {
            "analysis": analysis[1].toDict(),
            "name": hashtag,
            "tweets": analysis[0],
            "n_entries": len(analysis[0])
        }
        entries += hashtag_data["n_entries"]
        hashtag_list.append(hashtag_data)
    analysis = dict()
    for key in list(hashtag_list[0]["analysis"].keys()):
        analysis[key] = mean([hashtag["analysis"][key] for hashtag in hashtag_list])
    return jsonify({
        "analysis": analysis,
        "hashtags":hashtag_list,
        "n_entries":entries
    })

if __name__ == "__main__":
    app.run("127.0.0.1", os.getenv("PORT"), debug=bool(os.getenv("DEBUG")))


