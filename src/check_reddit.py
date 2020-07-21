import os
import praw
import json
import time
import pickle
from typing import List, Dict
from dictionary import get_dictionary
from sheet import str_to_sheet
from models.base import Analysis
from models.reddit import RedditWrapper, RedditAnalyzer, Submission, Redditor, Subreddit
import pandas as pd
from uuid import uuid4
from random import randint

# Modificar según directorio de ejecución
dict_path = "./data/diccionario.json"
submissions_path = "./data/submissions.dat"
client_ids = ["qXZ7TecmK3wXyA", "AUs7RM1sxg8Itg", "HzCPQ9tBASR0GQ", "giyavhV0KeKIWQ"]
client_secrets = ["TFFl-kNXgPM6_dDzv3UtxJZI72w", "NVkkQtixo7aMWnDjGqi8fCmUP_g", "Bc9k1oO0t8yt0nyc0wX4b-8zA7M", "ZP2ESB70J791295mdmaGA6C2Nhg"]
index = randint(0,3)
dictionary = get_dictionary(dict_path)
reddit = praw.Reddit(client_id=client_ids[index], user_agent="my user agent", client_secret=client_secrets[index])
rwrapper = RedditWrapper(reddit, RedditAnalyzer(dictionary))

# Comentar luego de prueba inicial

amounts = [5, 10, 50, 100, 200]

# Descomentar después de prueba inicial (cantidad máxima estimada de submissions: 51000)
#amounts = [50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]

if __name__ == "__main__":
    with open(submissions_path, "rb") as subfile:
        stamp = time.strftime("%H:%M")
        print(f"[{stamp}] Cargando entradas...")
        submissions: List[Submission] = pickle.load(subfile)
        stamp = time.strftime("%H:%M")
        print(f"[{stamp}] Entradas cargadas con éxito")
        print(f"[{stamp}] Iniciando análisis...")
        length = len(submissions)
        studies: List[float] = []
        for amount in amounts:
            if(length >= amount):
                stamp = time.strftime("%H:%M")
                print(f"[{stamp}] Analizando {amount} registros...")
                start = time.time()
                analysis = rwrapper.analyzer.analyze_submissions(submissions[0: amount], False, True)[0]
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
        filename = f"reddit-test-{str(uuid4()).split('-')[0]}.xlsx"
        df.to_excel(filename)
        stamp = time.strftime("%H:%M")
        print(f"[{stamp}] Archivo {filename} creado con éxito!")
