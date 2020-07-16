import os
from dictionary import get_dictionary
from sheet import str_to_sheet
from flask import Flask, request, jsonify, Response, send_file
from werkzeug.datastructures import FileStorage
from flask_cors import CORS
from models.base import Analysis
from models.reddit import RedditWrapper, RedditAnalyzer, Submission, Redditor
from models.twitter import TwitterData, TwitterStreamer, TwitterClient, TwitterAnalyzer
from tweepy import OAuthHandler
from typing import List, IO
import tweepy
import praw
from translate import Translator

app = Flask(__name__)
translator= Translator(to_lang="Spanish")
CORS(app)
dictionary = get_dictionary('./data/diccionario.json')
reddit = praw.Reddit(client_id="AUs7RM1sxg8Itg", user_agent="my user agent", client_secret="NVkkQtixo7aMWnDjGqi8fCmUP_g")
rwrapper = RedditWrapper(reddit, RedditAnalyzer(dictionary))


@app.route('/reddit/user', methods=["GET", "POST"])
def get_reddit_users():
    names: List[str] = []
    if request.method == "GET":
        names = ["joeyisgoingto", "antikarma98", "Frustration", "Ginger_Lupus", "BreakfastforDinner"]
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
        names = ["golang", "Fitness", "lectures", "videogames", "politics", "Paranormal"]
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

@app.route('/twitter/user/<name>')
def get_twitter_user(name: str):
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    user = api.get_user(name)
    user_data = {
        "id": user.id,
        "name": user.name,
        "screen_name": user.screen_name,
        "description": user.description,
        "location": user.location,
        "friends_count": user.friends_count,
        "followers_count": user.followers_count,
        "created_at": user.created_at,
        "verified": user.verified,
        "text": user.status.text
    }
    # return jsonify({"user": user._json})
    return jsonify({"user": user_data})

@app.route('/twitter/hashtag/<hashtag>')
def get_twitter_hashtag(hashtag: str):
    twitter_client = TwitterClient()

    hashtag_tweets = twitter_client.get_hashtag_tweets_to_analyze(hashtag)
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

    return jsonify({"Tweets":hashtag_tweets,
        "Autoconciencia":autoconciencia_emocional,
        "Autoestima": autoestima,
        "Comprensión Organizativa": comprension_organizativa,
        "Comunicación Asertiva": comunicacion_asertiva,
        "Conciencia Crítica": conciencia_critica,
        "Motivación de logro": motivacion_de_logro,
        "Tolerancia": tolerancia,
        "Desarrollar y estimular a los demas": desarrollar_y_estimular_a_los_demas,
        "Empatia": empatia,
        "Colaboración y Cooperación": colaboracion_cooperacion,
        "Percepción y Comprensión emocional": percepcion_comprension_emocional

     })
    #return jsonify({"hashtag": api._json})

@app.route('/twitter/tweets/<tweet_id>')
def get_tweet(tweet_id: str):
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
    return jsonify({"Tweets":text_tweets,
        "Autoconciencia":autoconciencia_emocional,
        "Autoestima": autoestima,
        "Comprensión Organizativa": comprension_organizativa,
        "Comunicación Asertiva": comunicacion_asertiva,
        "Conciencia Crítica": conciencia_critica,
        "Motivación de logro": motivacion_de_logro,
        "Tolerancia": tolerancia,
        "Desarrollar y estimular a los demas": desarrollar_y_estimular_a_los_demas,
        "Empatia": empatia,
        "Colaboración y cooperación": colaboracion_cooperacion,
        "Percepción y Comprensión emocional": percepcion_comprension_emocional
        #"Liderazgo": liderazgo
     })


@app.route('/twitter/tweets/user/<name>')
def get_tweets(name: str):
    twitter_client = TwitterClient()
    text_tweets = twitter_client.get_tweets_to_analyze(name)
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
    return jsonify({"Tweets":text_tweets,
        "Autoconciencia":autoconciencia_emocional,
        "Autoestima": autoestima,
        "Comprensión Organizativa": comprension_organizativa,
        "Comunicación Asertiva": comunicacion_asertiva,
        "Conciencia Crítica": conciencia_critica,
        "Motivación de logro": motivacion_de_logro,
        "Tolerancia": tolerancia,
        "Desarrollar y estimular a los demas": desarrollar_y_estimular_a_los_demas,
        "Empatia": empatia,
        "Colaboración y cooperación": colaboracion_cooperacion,
        "Percepción y Comprensión emocional": percepcion_comprension_emocional
        #"Liderazgo": liderazgo
     })

     
#@app.route('/twitter')
#def get_tweet():
#    twitter_client = TwitterClient()
#    api = twitter_client.get_twitter_client_api()
#    user = api.get_user("2LarryJohnson7")
#    tweets = api.user_timeline(user.id)
#    tweet : tweepy.models.Status = tweets[0]
#    #tws = [tweet for tweet in tweets]
#    #for tw in tws:
#    #    print(tw.text)
#    #replies = tweepy.Cursor(api.search, q=f"to:{'2LarryJohnson7'}", since_id=tws[2].id, tweet_mode="extended").items()
#    #for reply in replies:
#    #    pass
#    return jsonify({"msg" : tweet._json})



if __name__ == "__main__":
    app.run("127.0.0.1", "5000", debug=True)
