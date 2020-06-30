from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor

#import numpy as np
#import pandas as pd

class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_hashtag(self, twitter_hashtag):
        hashtags = []
        for tweet in Cursor(self.twitter_client.search, q=twitter_hashtag, result_type='recent').items(10):
            hashtags.append({
                "id": tweet.id,
                "text": tweet.text
            })
        hashtag_data = {
            "hashtags" : hashtags,
            "hashtag_name": twitter_hashtag,
            "n_entries" : len(hashtags)
        }
        return hashtag_data

    def get_tweet(self, name):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, screen_name=name).items(10):
            tweets.append({
            "id": tweet.id,
            "text": tweet.text
            }) 
        tweet_data = {
            "tweets": tweets,
            "user":name,
            "n_entries": len(tweets)
        }
        return tweet_data
        
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


class TweetAnalyzer():
    pass
"""     def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['favorite_count'] = np.array([tweet.favorite_count for tweet in tweets])
        #df['retweets'] = np.array([tweet.retweets for tweet in tweets])
        df['created_at'] = np.array([tweet.created_at for tweet in tweets])
        #df['favorite'] = np.array([tweet.favorite for tweet in tweets])
        df['user'] = np.array([tweet.user for tweet in tweets])
        #df['author'] = np.array([tweet.author for tweet in tweets])
        #df['favorited'] = np.array([tweet.favorited for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        #df['retweet'] = np.array([tweet.retweet for tweet in tweets])
        df['retweet_count'] = np.array([tweet.retweet_count for tweet in tweets])
        #df['retweeted'] = np.array([tweet.retweeted for tweet in tweets])
        #df['retweeted_status'] = np.array([tweet.retweeted_status for tweet in tweets])
        #df['text'] = np.array([tweet.text for tweet in tweets])
        #df['geo'] = np.array([tweet.geo for tweet in tweets])
        #df['in_reply_to_status_id'] = np.array([tweet.in_reply_to_status_id for tweet in tweets])
        #df['in_reply_to_screen_name'] = np.array([tweet.in_reply_to_screen_name for tweet in tweets])

        return df

    def data_frame_to_csv(self, dataFrame):
        dataFrame.to_csv('../../data/tweets.csv', encoding='utf-8')
        return 'success' """
