from dictionary import get_dictionary
from flask import Flask, request, jsonify
from models.reddit import RedditWrapper, RedditAnalyzer
from models.twitter import TwitterData, TwitterStreamer, TwitterClient
from tweepy import OAuthHandler
import praw

app = Flask(__name__)
dictionary = get_dictionary('./data/diccionario.json')
reddit = praw.Reddit(client_id="AUs7RM1sxg8Itg", user_agent="my user agent", client_secret="NVkkQtixo7aMWnDjGqi8fCmUP_g")
rwrapper = RedditWrapper(reddit, RedditAnalyzer(dictionary))

@app.route('/reddit')
def get_reddit_user():
    user_id = request.args.get('user')
    analysis = rwrapper.analyze_user_by_id(user_id)
    return jsonify(analysis.toDict())

@app.route('/twitter')
def get_tweet():

    # test para tweets que contengan estos campos
    hast_tag_list = ['donald tump']
    fetched_tweets_filename = "tweets.txt"

    # si TwitterClient esta vacío muestra los tweets de mi twitter que hice que esta vacío
    # al agregar el nombre de usuario de cualquier persona se mostrara por consola toda la info
    
    twitter_client = TwitterClient('PhilCollinsFeed')
    # twitter_client = TwitterClient()

   # twitter_streamer = TwitterStreamer()
   # twitter_streamer.stream_tweets(fetched_tweets_filename, hast_tag_list)

    # cantidad de tweets a imprimir
    print(twitter_client.get_user_timeline_tweets(1))

    return 'success'
    
    # return stream

if __name__ == "__main__":
    app.run("127.0.0.1", "5000", debug=True)