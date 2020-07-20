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

@app.route('/twitter/hashtags/<hashtag>')
def get_twitter_hashtag(hashtag: str):
    twitter_client = TwitterClient()

    hashtag_tweets = twitter_client.get_hashtag_tweets_to_analyze("#" + hashtag)
    twitter_analyzer = TwitterAnalyzer(dictionary)

    autoconciencia_emocional = twitter_analyzer.get_autoconciencia_by_group(hashtag_tweets)
    autoestima = twitter_analyzer.get_autoestima_by_group(hashtag_tweets)
    comprension_organizativa = twitter_analyzer.get_comprension_by_group(hashtag_tweets)
    comunicacion_asertiva = twitter_analyzer.get_comunicacion_asertiva_by_group(hashtag_tweets)
    conciencia_critica = twitter_analyzer.get_conciencia_critica_by_group(hashtag_tweets)
    motivacion_de_logro = twitter_analyzer.get_motivacion_by_group(hashtag_tweets, 'hashtag')
    tolerancia = twitter_analyzer.get_tolerancia_by_group(hashtag_tweets, 'hashtag')
    desarrollar_y_estimular_a_los_demas = twitter_analyzer.get_desarrollar_by_group_user(hashtag_tweets)
    empatia = twitter_analyzer.get_empatia_by_group_user(hashtag_tweets)
    colaboracion_cooperacion = twitter_analyzer.get_collaboration_cooperation_by_group(hashtag_tweets, 'hashtag')
    percepcion_comprension_emocional = twitter_analyzer.get_percepcion_comprension_emocional_by_group(hashtag_tweets, 'hashtag')

    analysis = Analysis(
        autoconciencia_emocional=autoconciencia_emocional,autoestima=autoestima,
        comprension_organizativa=comprension_organizativa, asertividad=comunicacion_asertiva,
        conciencia_critica=conciencia_critica,motivacion_logro=motivacion_de_logro,
        tolerancia_frustracion=tolerancia,desarrollo_relaciones=desarrollar_y_estimular_a_los_demas,
        empatia=empatia, colaboracion_cooperacion=colaboracion_cooperacion, percepcion_compresion_emocional=percepcion_comprension_emocional)

    return jsonify({
        "name": hashtag,
        "tweets": hashtag_tweets,
        "analysis": analysis.toDict(),
        "n_entries": len(hashtag_tweets)
    })

@app.route('/twitter/user/<name>')
def get_tweets(name: str):
    twitter_client = TwitterClient()
    text_tweets = twitter_client.get_tweets_to_analyze(name)
    twitter_analyzer = TwitterAnalyzer(dictionary)

    user = twitter_client.twitter_client.get_user(name)

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
    #liderazgo = twitter_analyzer.get_liderazgo_by_group_user()

    analysis = Analysis(
        autoconciencia_emocional=autoconciencia_emocional,autoestima=autoestima,
        comprension_organizativa=comprension_organizativa, asertividad=comunicacion_asertiva,
        conciencia_critica=conciencia_critica,motivacion_logro=motivacion_de_logro,
        tolerancia_frustracion=tolerancia,desarrollo_relaciones=desarrollar_y_estimular_a_los_demas,
        empatia=empatia, colaboracion_cooperacion=colaboracion_cooperacion, percepcion_compresion_emocional=percepcion_comprension_emocional)

    return jsonify({
        "user": user._json,
        "tweets": text_tweets,
        "analysis" : analysis.toDict(),
        "n_entries": len(text_tweets)
     })

@app.route('/twitter/analyze-tweet', methods=["POST"])
def get_tweet():
    data = request.json
    if "tweet_id" not in data:
        return Response("", status=400)
    tweet_id = data["tweet_id"]
    twitter_client = TwitterClient()
    tweets_ids = [tweet_id]
    text_tweets = twitter_client.get_tweet_to_analyze(tweets_ids)
    twitter_analyzer = TwitterAnalyzer(dictionary)

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
    #liderazgo = twitter_analyzer.get_liderazgo_by_group_user()

    analysis = Analysis(
        autoconciencia_emocional=autoconciencia_emocional,autoestima=autoestima,
        comprension_organizativa=comprension_organizativa, asertividad=comunicacion_asertiva,
        conciencia_critica=conciencia_critica,motivacion_logro=motivacion_de_logro,
        tolerancia_frustracion=tolerancia,desarrollo_relaciones=desarrollar_y_estimular_a_los_demas,
        empatia=empatia, colaboracion_cooperacion=colaboracion_cooperacion, percepcion_compresion_emocional=percepcion_comprension_emocional)

    return jsonify({
        "analysis" : analysis.toDict()
    })

if __name__ == "__main__":
    app.run("127.0.0.1", os.getenv("PORT"), debug=bool(os.getenv("DEBUG")))


