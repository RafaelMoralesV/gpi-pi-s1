import io
from models.base import Analysis, BaseAnalyzer, BaseAPIWrapper
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
from textblob import TextBlob
from googletrans import Translator

class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    '''
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

    def get_hashtag_tweets(self, twitter_hashtag):
        tweets_hashtag = []
        for tweet in Cursor(self.twitter_client.search, q=twitter_hashtag, result_type='recent').items(10):
            tweets_hashtag.append({
                "text": tweet.text
            })
        return tweets_hashtag
    '''

    def get_hashtag_tweets_to_analyze(self, twitter_hashtag):
        tweets = []        
        translator = Translator()
        for tweet in Cursor(self.twitter_client.search, q=twitter_hashtag, count=50, tweet_mode='extended').items(50):
        	traduce = translator.translate(tweet.full_text,dest='en')
        	if(TextBlob(traduce.text).subjectivity != 0 and TextBlob(traduce.text).sentiment.polarity != 0):
        		tweets.append({
        			"id" : tweet.id,
        			"retweeted" : tweet.retweeted,
        			"retweet_count " : tweet.retweet_count,
        			"text" : traduce.text,
                    "likes" : tweet.favorite_count
        		})
        
        return tweets


    '''    
    def get_tweet(self, name):#tweets user
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
    
    def get_text_tweet(self, name):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, screen_name=name).items(10):
            tweets.append({
                "text": tweet.text
            })
        return tweets
        tweepy.Cursor(api.search, q="#"+hashtag, rpp=10).items(limit=15)
    '''
    
    def get_tweets_to_analyze(self, name):
        tweets = []        
        translator = Translator()
        for tweet in Cursor(self.twitter_client.user_timeline, screen_name=name, count=50, tweet_mode="extended").items(limit=50):
        	traduce = translator.translate(tweet.full_text,dest='en')
        	if(TextBlob(traduce.text).subjectivity != 0 and TextBlob(traduce.text).sentiment.polarity != 0):
        		tweets.append({
        			"id" : tweet.id,
        			"retweeted" : tweet.retweeted,
        			"retweet_count " : tweet.retweet_count,
        			"text" : traduce.text,
                    "likes" : tweet.favorite_count
        		})
        return tweets

    # timeline de los tweets
    '''
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
            print(tweets)
        return tweets
	'''

    def get_tweet_to_analyze(self, tweet_id):
        tweets = []
        tweet = self.twitter_client.statuses_lookup(tweet_id)
        tweets.append({
            "id" : tweet[0].id,
        	"retweeted" : tweet[0].retweeted,
        	"retweet_count " : tweet[0].retweet_count,
        	"text" : tweet[0].text,
            "likes" : tweet[0].favorite_count
        })
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


class TwitterAnalyzer(BaseAnalyzer):


    #Autoconciencia emocional

    def get_autoconciencia_by_group(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_autoconciencia_by_text(str(tweet["text"]),int(tweet["likes"]))
        promedio = promedio / len(tweets)
        return promedio

    def get_autoconciencia_by_text(self, text: str, likes: int):
        blob = TextBlob(text)
        #translator = Translator()
        #blob = translator.translate(text,dest='en')
        #blob = TextBlob(blob.text)
        subj = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'autoconciencia_emocional')
        match_score = matches*6 if matches <= 5 else 30
        score = subj*70 + match_score
        return score 


    # Autoestima

    def get_autoestima_by_group(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_autoestima_by_text(str(tweet["text"]))
        promedio = promedio / len(tweets)
        return promedio

    def get_autoestima_by_text(self, text: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'autoestima')
        match_score = matches * 6 if matches <= 10 else 60
        score = subj*40 + match_score
        return score


    # Comprensión Organizativa

    def get_comprension_by_group(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_comprension_by_text(str(tweet["text"]))
        return promedio/len(tweets)
    
    def get_comprension_by_text(self, text: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subj = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'comprension_organizativa')
        match_score = matches*2 if matches <= 10 else 20
        score = pol*60 + subj*20 + match_score
        return score

    
    # Comunicación Asertiva

    def get_comunicacion_asertiva_by_group(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_comunicacion_asertiva_by_text(str(tweet["text"]))
        return promedio/len(tweets)
    
    def get_comunicacion_asertiva_by_text(self, text: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subj = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'comunicacion_asertiva')
        match_score = matches*3 if matches <= 10 else 30
        score = pol*20 + subj*50 + match_score
        return score


    # Conciencia Crítica

    def get_conciencia_critica_by_group(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_conciencia_critica_by_text(str(tweet["text"]))
        return promedio/len(tweets)
    
    def get_conciencia_critica_by_text(self, text: str):
        blob = TextBlob(text)
        pol = blob.sentiment.polarity if blob.sentiment.polarity >= 0 else 0
        subj = blob.sentiment.subjectivity
        matches = self.match_factor_dict(text.lower(), 'conciencia_critica')
        match_score = matches*3 if matches <= 10 else 30
        score = pol*20 + subj*50 + match_score
        #print("CCRITICA  Pol: ",pol," Subj: ",subj," Match: ",match_score, "score", score)
        return score
    
    #Motivacion de logro

    def get_motivacion_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_motivacion_by_text(str(tweet["text"]), tipo)
        promedio = promedio / len(tweets)
        return promedio

    def get_motivacion_by_text(self,text:str, tipo:str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'motivacion_de_logro')
        if(tipo == 'usuario'):
            match_score = 0.5 if matches >=5 else matches*0.1
            score = (pol * 0.4 + subjectivity * 0.1 + match_score)*100 # porcentajes distintos en el pdf(?)
        elif(tipo == 'hashtag'):
            match_score = 0.5 if matches >=5 else matches*0.1
            score = (pol * 0.3 + subjectivity * 0.2 + match_score)*100
        return score
  

    #Tolerancia a la frustracion
    
    def get_tolerancia_by_text(self, text: str, tipo: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >=0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'tolerancia_a_la_frustracion')
        if(tipo == 'usuario'):
            match_score = 0.4 if matches >= 5 else matches * 0.08
            score = (pol*0.4 + subjectivity *0.2 + match_score)*100
        elif(tipo == 'hashtag'):
            match_score = 0.2 if matches >= 5 else matches * 0.04
            score = (pol*0.5 + subjectivity *0.3 + match_score)*100
        return score
    
    def get_tolerancia_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_tolerancia_by_text(str(tweet["text"]), tipo)
        promedio = promedio / len(tweets)
        return promedio 
    

   
    # Desarrollar y estimular a los demas 
    def get_desarrollar_by_text_user(self, text: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >=0 else 0
        matches = self.match_factor_dict(text.lower(), 'desarrollar_y_estimular_a_los_demas')
        match_score = 0.1 if matches >= 5 else matches * 0.02
        score = (pol*0.9 + match_score)*100
        return score

    def get_desarrollar_by_group_user(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_desarrollar_by_text_user(str(tweet["text"]))
        promedio = promedio / len(tweets)
        return promedio 
    

    #Empatia 
    def get_empatia_by_text_user(self, text: str, likes: int):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subj = blob.subjectivity
        likes_score = 50 if likes > 50 else 0
        matches = self.match_factor_dict(text.lower(), 'empatia')
        match_score = matches*10 if matches <= 3 else 50
        score = pol*0.2+subj*0.2+match_score+likes_score*0.2
        return score

    def get_empatia_by_group_user(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_empatia_by_text_user(str(tweet["text"]),int(tweet["likes"]))
        promedio = promedio / len(tweets)
        return promedio

    # Colaboración y cooperacion
    def get_collaboration_cooperation_by_text(self, text: str, retweet: int, tipo: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(text.lower(), 'colaboracion_cooperacion')
        if(tipo == 'user'):
            retweet_score = 10 if retweet >= 10 else 0
            match_score = matches if matches >= 3 else 0
        elif(tipo == 'hashtag'):
            retweet_score = 80 if retweet >= 80 else 0
            match_score = matches if matches >= 10 else 0
        
        score = pol*0.2+retweet_score*0.3+match_score*0.5
        return score

    def get_collaboration_cooperation_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_collaboration_cooperation_by_text(str(tweet["text"]),int(tweet["retweet_count "]), tipo)
        promedio = promedio / len(tweets)
        return promedio

    # Percepcion y comprension emocional
    def get_percepcion_comprension_emocionaln_by_text(self, text: str, likes: int, tipo: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(text.lower(), 'percepcion_comprension_emocional')
        if(tipo == 'user'):
            likes_score = 20 if likes >= 20 else 0
            match_score = matches if matches >= 3 else 0
        elif(tipo == 'hashtag'):
            likes_score = 100 if likes >= 100 else 0
            match_score = matches if matches >= 10 else 0
        
        score = pol*0.2+subj*0.2+likes_score*0.1+match_score*0.5
        return score

    def get_percepcion_comprension_emocional_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_percepcion_comprension_emocionaln_by_text(str(tweet["text"]),int(tweet["likes"]), tipo)
        promedio = promedio / len(tweets)
        return promedio

    pass



'''
    # Liderazgo
    def get_liderazgo_by_text_user(self, text: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >=0 else 0
        matches = self.match_factor_dict(text.lower(), 'liderazgo')
        match_score = 0.1 if matches >= 5 else matches * 0.02
        score = (pol*0.9 + match_score)*100
        return score

    def get_liderazgo_by_group_user(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_liderazgo_by_text_user(str(tweet))
        promedio = promedio / len(tweets)
        return promedio 
'''


#class TwitterWrapper(BaseAPIWrapper):
 #   analyzer: TwitterAnalyzer
 #   twitter_client: TwitterClient
 #   def __init__(self, client : TwitterClient ,analyzer: TwitterAnalyzer):
  #      self.analyzer = analyzer
  #      self.reddit = reddit
    

    



"""
class TweetAnalyzer():
    pass
     def tweets_to_data_frame(self, tweets):
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
