from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor

class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user
    # timeline de los tweets
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
            print(tweets)
        return tweets


class TwitterAuthenticator():
    # autenticador con las credenciales
    def authenticate_twitter_app(self):
        auth = OAuthHandler('Nj7SUk7Z6ZlHIixLNZDEw8tWt', 'y5xXNXxMK5P3QQUFpte28cUL7VIOiHViI0qsuECP5gbD07B6PN')
        auth.set_access_token('1262515401138847746-L46mzlO4lZiLntqiWMnYHMQ7QzrH1g', 'FCEkm1G3AdUBwMFNezJntLq3pVOcBbE8DdVcsqfrQoatE')
        return auth

class TwitterStreamer():

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        listener = TwitterData(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()

        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)


class TwitterData(StreamListener):

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
                return True
        except BaseException as e:
            print("Error: $s" % str(e))
        return True
    
    def on_error(self, status):
        if status == 420:
            return False
        print(status)
