import io
import time
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

    def get_hashtag_tweets_to_analyze(self, twitter_hashtag):
        tweets = []
        translator = Translator()
        for tweet in Cursor(self.twitter_client.search, q=twitter_hashtag, count=50, tweet_mode='extended').items(50):
            traduce = translator.translate(tweet.full_text, dest='en')
            tweet = tweet._json
            if(TextBlob(traduce.text).subjectivity != 0 and TextBlob(traduce.text).sentiment.polarity != 0):
                tweets.append({
                    "id": str(tweet["id"]),
                    "retweeted": tweet["retweeted"],
                    "retweet_count ": tweet["retweet_count"],
                    "text": tweet["full_text"],
                    "likes": tweet["favorite_count"]
                })
        return tweets

    def get_tweets_to_analyze(self, name):
        tweets = []
        translator = Translator()
        for tweet in Cursor(self.twitter_client.user_timeline, screen_name=name, count=50, tweet_mode="extended").items(limit=50):
            traduce = translator.translate(tweet.full_text, dest='en')
            tweet = tweet._json
            if(TextBlob(traduce.text).subjectivity != 0 and TextBlob(traduce.text).sentiment.polarity != 0):
                tweets.append({
                    "id": str(tweet["id"]),
                    "retweeted": tweet["retweeted"],
                    "retweet_count ": tweet["retweet_count"],
                    "text": traduce.text,
                    "likes": tweet["favorite_count"]
                })
        return tweets

    def get_tweet_to_analyze(self, tweet_id):
        tweets = []
        tweet = self.twitter_client.get_status(tweet_id[0])._json
        tweets.append({
            "id": str(tweet["id"]),
            "retweeted": tweet["retweeted"],
            "retweet_count ": tweet["retweet_count"],
            "text": tweet["text"],
            "likes": tweet["favorite_count"]
        })
        return tweets


class TwitterAuthenticator():
    
    def authenticate_twitter_app(self):
        auth = OAuthHandler('Nj7SUk7Z6ZlHIixLNZDEw8tWt',
                            'y5xXNXxMK5P3QQUFpte28cUL7VIOiHViI0qsuECP5gbD07B6PN')
        auth.set_access_token('1262515401138847746-L46mzlO4lZiLntqiWMnYHMQ7QzrH1g',
                              'FCEkm1G3AdUBwMFNezJntLq3pVOcBbE8DdVcsqfrQoatE')
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

    # Autoconciencia emocional

    def get_autoconciencia_by_group(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_autoconciencia_by_text(
                str(tweet["text"]), int(tweet["likes"]))
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    def get_autoconciencia_by_text(self, text: str, likes: int):
        blob = TextBlob(text)  
        subj = blob.subjectivity
        matches = self.match_factor_dict(
            text.lower(), 'autoconciencia_emocional')
        match_score = matches*6 if matches <= 5 else 30
        score = subj*70 + match_score
        return score

    # Autoestima

    def get_autoestima_by_group(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_autoestima_by_text(str(tweet["text"]))
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
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
        return promedio/len(tweets) if len(tweets) > 0 else 0

    def get_comprension_by_text(self, text: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subj = blob.subjectivity
        matches = self.match_factor_dict(
            text.lower(), 'comprension_organizativa')
        match_score = matches*2 if matches <= 10 else 20
        score = pol*60 + subj*20 + match_score
        return score

    # Comunicación Asertiva

    def get_comunicacion_asertiva_by_group(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_comunicacion_asertiva_by_text(
                str(tweet["text"]))
        return promedio/len(tweets) if len(tweets) > 0 else 0

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
        return promedio/len(tweets) if len(tweets) > 0 else 0

    def get_conciencia_critica_by_text(self, text: str):
        blob = TextBlob(text)
        pol = blob.sentiment.polarity if blob.sentiment.polarity >= 0 else 0
        subj = blob.sentiment.subjectivity
        matches = self.match_factor_dict(text.lower(), 'conciencia_critica')
        match_score = matches*3 if matches <= 10 else 30
        score = pol*20 + subj*50 + match_score
        #print("CCRITICA  Pol: ",pol," Subj: ",subj," Match: ",match_score, "score", score)
        return score

    # Motivacion de logro

    def get_motivacion_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_motivacion_by_text(str(tweet["text"]), tipo)
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    def get_motivacion_by_text(self, text: str, tipo: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'motivacion_de_logro')
        if(tipo == 'usuario'):
            match_score = 0.5 if matches >= 5 else matches*0.1
            score = (pol * 0.4 + subjectivity * 0.1 + match_score) * \
                100  # porcentajes distintos en el pdf(?)
        elif(tipo == 'hashtag'):
            match_score = 0.5 if matches >= 5 else matches*0.1
            score = (pol * 0.3 + subjectivity * 0.2 + match_score)*100
        return score

    # Tolerancia a la frustracion

    def get_tolerancia_by_text(self, text: str, tipo: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(
            text.lower(), 'tolerancia_a_la_frustracion')
        if(tipo == 'usuario'):
            match_score = 0.4 if matches >= 5 else matches * 0.08
            score = (pol*0.4 + subjectivity * 0.2 + match_score)*100
        elif(tipo == 'hashtag'):
            match_score = 0.2 if matches >= 5 else matches * 0.04
            score = (pol*0.5 + subjectivity * 0.3 + match_score)*100
        return score

    def get_tolerancia_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_tolerancia_by_text(str(tweet["text"]), tipo)
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    # Desarrollar y estimular a los demas

    def get_desarrollar_by_text_user(self, text: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(
            text.lower(), 'desarrollar_y_estimular_a_los_demas')
        match_score = 0.1 if matches >= 5 else matches * 0.02
        score = (pol*0.9 + match_score)*100
        return score

    def get_desarrollar_by_group_user(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_desarrollar_by_text_user(str(tweet["text"]))
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    # Empatia

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
            promedio += self.get_empatia_by_text_user(
                str(tweet["text"]), int(tweet["likes"]))
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    # Colaboración y cooperacion
    def get_collaboration_cooperation_by_text(self, text: str, retweet: int, tipo: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(
            text.lower(), 'colaboracion_cooperacion')
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
            promedio += self.get_collaboration_cooperation_by_text(
                str(tweet["text"]), int(tweet["retweet_count "]), tipo)
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    # Percepcion y comprension emocional
    def get_percepcion_comprension_emocionaln_by_text(self, text: str, likes: int, tipo: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(
            text.lower(), 'percepcion_comprension_emocional')
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
            promedio += self.get_percepcion_comprension_emocionaln_by_text(
                str(tweet["text"]), int(tweet["likes"]), tipo)
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    # Manejo de Conflictos

    def get_manejo_de_conflictos_by_text(self, text: str, likes: int, tipo: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        pol = blob.polarity if blob.polarity >= 0 else 0
        hashtag_score = 0
        full_text = text.split()
        for word in full_text:
            if('#' in word):
                search_word = word.replace('#', '')
                hashtag_score += self.match_factor_dict(
                    search_word.lower(), 'manejo_de_conflictos')
        matches = self.match_factor_dict(text.lower(), 'manejo_de_conflictos')
        if(tipo == 'user'):
            hashtag_score = 10 if hashtag_score > 10 else 0
            likes_score = 100 if likes > 100 else 0
            match_score = 20 if matches > 20 else 0
            score = pol*5+subj*5+0.1*likes_score*0.1+match_score+hashtag_score*6
        elif(tipo == 'hashtag'):
            match_score = 30 if matches > 30 else 0
            score = pol*40+subj*30+match_score

        return score

    def get_manejo_de_conflictos_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_manejo_de_conflictos_by_text(
                str(tweet["text"]), int(tweet["likes"]), tipo)
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    # Violencia
    def get_violencia_by_text(self, text: str, likes: int, tipo: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        pol = blob.polarity if blob.polarity < 0 else 0
        hashtag_score = 0
        full_text = text.split()
        for word in full_text:
            if('#' in word):
                search_word = word.replace('#', '')
                hashtag_score += self.match_factor_dict(
                    search_word.lower(), 'violencia')
        matches = self.match_factor_dict(text.lower(), 'violencia')
        if(tipo == 'user'):
            hashtag_score = 10 if hashtag_score > 10 else 0
            likes_score = 100 if likes > 100 else 0
            match_score = 20 if matches > 20 else 0
            score = pol*5+subj*5+0.25*likes_score*0.1+match_score+hashtag_score*50
        elif(tipo == 'hashtag'):
            match_score = 30 if matches > 30 else 0
            score = pol*30+subj*40+match_score

        return score

    def get_violencia_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_violencia_by_text(
                str(tweet["text"]), int(tweet["likes"]), tipo)
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    # Relación Social
    def get_relacion_social_by_text(self, text: str, likes: int, tipo: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        pol = blob.polarity if blob.polarity >= 0 else 0
        hashtag_score = 0
        full_text = text.split()
        for word in full_text:
            if('#' in word):
                search_word = word.replace('#', '')
                hashtag_score += self.match_factor_dict(
                    search_word.lower(), 'relacion_social')
        matches = self.match_factor_dict(text.lower(), 'relacion_social')
        if(tipo == 'user'):
            hashtag_score = 10 if hashtag_score > 10 else 0
            likes_score = 20 if likes > 20 else 0
            match_score = 20 if matches > 20 else 0
            score = pol*5+subj*5+0.5*likes_score*0.1+match_score+hashtag_score*6
        elif(tipo == 'hashtag'):
            match_score = 20 if matches > 20 else 0
            score = pol*30+subj*50+match_score

        return score

    def get_relacion_social_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_relacion_social_by_text(
                str(tweet["text"]), int(tweet["likes"]), tipo)
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    # Optimismo
    def get_optimismo_by_text(self, text: str, likes: int, tipo: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        pol = blob.polarity if blob.polarity >= 0 else 0
        hashtag_score = 0
        full_text = text.split()
        for word in full_text:
            if('#' in word):
                search_word = word.replace('#', '')
                hashtag_score += self.match_factor_dict(
                    search_word.lower(), 'optimismo')
        matches = self.match_factor_dict(text.lower(), 'optimismo')
        if(tipo == 'user'):
            hashtag_score = 10 if hashtag_score > 10 else 0
            match_score = 10 if matches > 10 else 0
            score = subj*80+match_score+hashtag_score
        elif(tipo == 'hashtag'):
            match_score = 10 if matches > 10 else 0
            score = pol*20+subj*70+match_score

        return score

    def get_optimismo_by_group(self, tweets: list, tipo: str):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_optimismo_by_text(
                str(tweet["text"]), int(tweet["likes"]), tipo)
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    pass

    # Liderazgo

    def get_liderazgo_by_text_user(self, text: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(text.lower(), 'liderazgo')
        match_score = 0.1 if matches >= 5 else matches * 0.02
        score = (pol*0.9 + match_score)*100
        return score

    def get_liderazgo_by_group_user(self, tweets: list):
        promedio = 0
        for tweet in tweets:
            promedio += self.get_liderazgo_by_text_user(str(tweet))
        promedio = promedio / len(tweets) if len(tweets) > 0 else 0
        return promedio

    def analyze_user_by_name(self, name: str, twitter_client: TwitterClient):
        text_tweets = twitter_client.get_tweets_to_analyze(name)
        autoconciencia_emocional = self.get_autoconciencia_by_group(
            text_tweets)
        autoestima = self.get_autoestima_by_group(text_tweets)
        comprension_organizativa = self.get_comprension_by_group(text_tweets)
        comunicacion_asertiva = self.get_comunicacion_asertiva_by_group(
            text_tweets)
        conciencia_critica = self.get_conciencia_critica_by_group(text_tweets)
        motivacion_de_logro = self.get_motivacion_by_group(
            text_tweets, 'usuario')
        tolerancia = self.get_tolerancia_by_group(text_tweets, 'usuario')
        desarrollar_y_estimular_a_los_demas = self.get_desarrollar_by_group_user(
            text_tweets)
        empatia = self.get_empatia_by_group_user(text_tweets)
        colaboracion_cooperacion = self.get_collaboration_cooperation_by_group(
            text_tweets, 'user')
        percepcion_comprension_emocional = self.get_percepcion_comprension_emocional_by_group(
            text_tweets, 'user')
        liderazgo = self.get_liderazgo_by_group_user(text_tweets)
        manejo_de_conflictos = self.get_manejo_de_conflictos_by_group(
            text_tweets, 'user')
        violencia = self.get_violencia_by_group(text_tweets, 'user')
        relacion_social = self.get_relacion_social_by_group(
            text_tweets, 'user')
        optimismo = self.get_optimismo_by_group(text_tweets, 'user')

        analysis = Analysis(
            autoconciencia_emocional=autoconciencia_emocional, autoestima=autoestima,
            comprension_organizativa=comprension_organizativa, asertividad=comunicacion_asertiva,
            conciencia_critica=conciencia_critica, motivacion_logro=motivacion_de_logro,
            tolerancia_frustracion=tolerancia, desarrollar_estimular=desarrollar_y_estimular_a_los_demas,
            empatia=empatia, colaboracion_cooperacion=colaboracion_cooperacion, percepcion_comprension_emocional=percepcion_comprension_emocional,
            manejo_conflictos=manejo_de_conflictos, violencia=violencia, relacion_social=relacion_social, optimismo=optimismo, liderazgo=liderazgo)
        return text_tweets, analysis

    def analyze_by_hashtag(self, hashtag: str, twitter_client: TwitterClient):
        hashtag_tweets = twitter_client.get_hashtag_tweets_to_analyze(
            "#" + hashtag)
        autoconciencia_emocional = self.get_autoconciencia_by_group(
            hashtag_tweets)
        autoestima = self.get_autoestima_by_group(hashtag_tweets)
        comprension_organizativa = self.get_comprension_by_group(
            hashtag_tweets)
        comunicacion_asertiva = self.get_comunicacion_asertiva_by_group(
            hashtag_tweets)
        conciencia_critica = self.get_conciencia_critica_by_group(
            hashtag_tweets)
        motivacion_de_logro = self.get_motivacion_by_group(
            hashtag_tweets, 'hashtag')
        tolerancia = self.get_tolerancia_by_group(hashtag_tweets, 'hashtag')
        desarrollar_y_estimular_a_los_demas = self.get_desarrollar_by_group_user(
            hashtag_tweets)
        empatia = self.get_empatia_by_group_user(hashtag_tweets)
        colaboracion_cooperacion = self.get_collaboration_cooperation_by_group(
            hashtag_tweets, 'hashtag')
        percepcion_comprension_emocional = self.get_percepcion_comprension_emocional_by_group(
            hashtag_tweets, 'hashtag')
        liderazgo = self.get_liderazgo_by_group_user(hashtag_tweets)
        manejo_de_conflictos = self.get_manejo_de_conflictos_by_group(
            hashtag_tweets, 'hashtag')
        violencia = self.get_violencia_by_group(hashtag_tweets, 'hashtag')
        relacion_social = self.get_relacion_social_by_group(
            hashtag_tweets, 'hashtag')
        optimismo = self.get_optimismo_by_group(hashtag_tweets, 'hashtag')

        analysis = Analysis(
            autoconciencia_emocional=autoconciencia_emocional, autoestima=autoestima,
            comprension_organizativa=comprension_organizativa, asertividad=comunicacion_asertiva,
            conciencia_critica=conciencia_critica, motivacion_logro=motivacion_de_logro,
            tolerancia_frustracion=tolerancia, desarrollar_estimular=desarrollar_y_estimular_a_los_demas,
            empatia=empatia, colaboracion_cooperacion=colaboracion_cooperacion, percepcion_comprension_emocional=percepcion_comprension_emocional,
            manejo_conflictos=manejo_de_conflictos, violencia=violencia, relacion_social=relacion_social, optimismo=optimismo, liderazgo=liderazgo)
        return hashtag_tweets, analysis

    def analyze_hashtag_tweets(self, tweets: list):
        autoconciencia_emocional = self.get_autoconciencia_by_group(tweets)
        autoestima = self.get_autoestima_by_group(tweets)
        comprension_organizativa = self.get_comprension_by_group(tweets)
        comunicacion_asertiva = self.get_comunicacion_asertiva_by_group(tweets)
        conciencia_critica = self.get_conciencia_critica_by_group(tweets)
        motivacion_de_logro = self.get_motivacion_by_group(tweets, 'hashtag')
        tolerancia = self.get_tolerancia_by_group(tweets, 'hashtag')
        desarrollar_y_estimular_a_los_demas = self.get_desarrollar_by_group_user(
            tweets)
        empatia = self.get_empatia_by_group_user(tweets)
        colaboracion_cooperacion = self.get_collaboration_cooperation_by_group(
            tweets, 'hashtag')
        percepcion_comprension_emocional = self.get_percepcion_comprension_emocional_by_group(
            tweets, 'hashtag')
        liderazgo = self.get_liderazgo_by_group_user(tweets)
        manejo_de_conflictos = self.get_manejo_de_conflictos_by_group(
            tweets, 'hashtag')
        violencia = self.get_violencia_by_group(tweets, 'hashtag')
        relacion_social = self.get_relacion_social_by_group(tweets, 'hashtag')
        optimismo = self.get_optimismo_by_group(tweets, 'hashtag')

        analysis = Analysis(
            autoconciencia_emocional=autoconciencia_emocional, autoestima=autoestima,
            comprension_organizativa=comprension_organizativa, asertividad=comunicacion_asertiva,
            conciencia_critica=conciencia_critica, motivacion_logro=motivacion_de_logro,
            tolerancia_frustracion=tolerancia, desarrollar_estimular=desarrollar_y_estimular_a_los_demas,
            empatia=empatia, colaboracion_cooperacion=colaboracion_cooperacion, percepcion_comprension_emocional=percepcion_comprension_emocional,
            manejo_conflictos=manejo_de_conflictos, violencia=violencia, relacion_social=relacion_social, optimismo=optimismo, liderazgo=liderazgo)
        return analysis

