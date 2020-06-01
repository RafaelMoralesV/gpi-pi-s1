from dictionary import get_dictionary
from flask import Flask, request, jsonify
from models.reddit import RedditWrapper, RedditAnalyzer
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

if __name__ == "__main__":
    app.run("127.0.0.1", "5000", debug=True)