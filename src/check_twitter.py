import os
import time
import pickle
import pandas as pd
from typing import List, Dict, Union
from uuid import uuid4
from dictionary import get_dictionary
from models.base import Analysis
from models.twitter import TwitterData, TwitterStreamer, TwitterClient, TwitterAnalyzer

# Modificar según directorio de ejecución
dict_path = "./data/diccionario.json"
tweets_path = "./data/tweets.dat"
dictionary = get_dictionary(dict_path)
twitter_client = TwitterClient()
twitter_analyzer = TwitterAnalyzer(dictionary)

# Comentar luego de prueba inicial

#amounts = [5, 10, 50, 100, 200]

# Descomentar después de prueba inicial (cantidad máxima estimada de submissions: 51000)
amounts = [50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]

if __name__ == "__main__":
    with open(tweets_path, "rb") as twfile:
        stamp = time.strftime("%H:%M")
        print(f"[{stamp}] Cargando tweets...")
        tweets: List[Dict[str, Union[str, int]]] = pickle.load(twfile)
        stamp = time.strftime("%H:%M")
        print(f"[{stamp}] Tweets cargados con éxito")
        print(f"[{stamp}] Iniciando análisis...")
        length = len(tweets)
        studies: List[float] = []
        for amount in amounts:
            if(length >= amount):
                stamp = time.strftime("%H:%M")
                print(f"[{stamp}] Analizando {amount} registros...")
                start = time.time()
                analysis = twitter_analyzer.analyze_hashtag_tweets(tweets[0: amount])
                end = time.time()
                elapsed = end - start
                danalysis = list(analysis.toDict().values())
                danalysis.append(elapsed)
                studies.append(danalysis)
        stamp = time.strftime("%H:%M")
        print(f"[{stamp}] Análisis Finalizado")
        columns = list(analysis.toDict().keys())
        columns.append("Duracion")
        df = pd.DataFrame(studies, index=amounts, columns=columns)
        filename = f"twitter-test-{str(uuid4()).split('-')[0]}.xlsx"
        df.to_excel(filename)
        stamp = time.strftime("%H:%M")
        print(f"[{stamp}] Archivo {filename} creado con éxito!")
