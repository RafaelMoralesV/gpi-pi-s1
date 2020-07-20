import os
import praw
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
from dictionary import get_dictionary
from sheet import str_to_sheet
from models.base import Analysis
from models.reddit import RedditWrapper, RedditAnalyzer, Submission, Redditor, Subreddit
import pandas as pd
from uuid import uuid4
from random import randint

# Modificar según directorio de ejecución
dict_path = "./data/diccionario.json"

client_ids = ["qXZ7TecmK3wXyA", "AUs7RM1sxg8Itg", "HzCPQ9tBASR0GQ", "giyavhV0KeKIWQ"]
client_secrets = ["TFFl-kNXgPM6_dDzv3UtxJZI72w", "NVkkQtixo7aMWnDjGqi8fCmUP_g", "Bc9k1oO0t8yt0nyc0wX4b-8zA7M", "ZP2ESB70J791295mdmaGA6C2Nhg"]
index = randint(0,3)
dictionary = get_dictionary(dict_path)
reddit = praw.Reddit(client_id=client_ids[index], user_agent="my user agent", client_secret=client_secrets[index])
rwrapper = RedditWrapper(reddit, RedditAnalyzer(dictionary))

# Comentar luego de prueba inicial

amounts = [5, 10, 50, 100]

default_reddit_subreddits = ["golang", "Futurology", "MemeEconomy"]

""" Descomentar luego de prueba inicial
amounts = [5, 10, 50, 100, 500, 1000, 2500, 5000, 10000, 50000, 100000]

default_reddit_subreddits = [
    "wacom",
    "WahoosTipi",
    "waifuism",
    "Wales",
    "wallpaperdump",
    "wallpaperengine",
    "walmart",
    "WalmartCelebrities",
    "waltonchain",
    "Waluigi",
    "wanchain",
    "wanttobelieve",
    "war",
    "WarCollege",
    "warcraftlore",
    "wardrobepurge",
    "WarframeRunway",
    "wargame",
    "wargroove",
    "Warhammer30k",
    "WarhammerCompetitive",
    "Warmachine",
    "WarplanePorn",
    "wartrade",
    "Washington",
    "wasletztepreis",
    "WaspHating",
    "watch_dogs",
    "WatchAnimalsDieInside",
    "WatchDogsWoofInside",
    "WatchesCirclejerk",
    "watchpeoplealmostdie",
    "WatchPeopleCode",
    "watchpeoplecrumble",
    "watchplantsgrow",
    "WatchRedditDie",
    "water",
    "waterbros",
    "watercolor101",
    "watercooling",
    "Waterisfuckingstupid",
    "waterloo",
    "Waxpen",
    "WayOfTheBern",
    "WC3",
    "WearOS",
    "weather",
    "WeatherPorn",
    "Web_Development",
    "web_programming",
    "webhosting",
    "webmarketing",
    "wec",
    "wedding",
    "weddingdress",
    "WeddingPhotography",
    "Weddingsunder10k",
    "weedbiz",
    "ween",
    "weezer",
    "WeHaveSeenTheButthole",
    "WeightLossAdvice",
    "weightwatchers",
    "WeinsteinEffect",
    "WeirdEggs",
    "WeirdFlexButOK",
    "WeirdLit",
    "weirdwikihow",
    "WeirdWings",
    "Wellington",
    "wendystwitter",
    "WEPES",
    "wesanderson",
    "WesternGifs",
    "Wetshaving",
    "wewantcups",
    "wewontcallyou",
    "WGU",
    "WhatAWeeb",
    "whatcarshouldIbuy",
    "Whatisthis",
    "whatsthatbook",
    "whatstheword",
    "whatsthisbird",
    "whatsthisrock",
    "whatsthisworth",
    "WhereAreAllTheGoodMen",
    "WhereIsAssange",
    "whereisthis",
    "Wheresthebottom",
    "whisky",
    "Whiskyporn",
    "WhiteHouseDinners",
    "whitepeoplefacebook",
    "whitesox",
    "WhiteWolfRPG",
    "WhoIsAmerica",
    "whole30",
    "wholesome",
    "Wholesome4chan",
    "Wholesomecringe",
    "wholesomefortnite",
    "wholesomejojo",
    "Wholesomenosleep",
    "wholesomeouija",
    "wholesomeoverwatch",
    "wholesomepranks",
    "wholesomeprequelmemes",
    "wholesomevandalism",
    "whoooosh",
    "whoosh",
    "whoselineisitanyway",
    "whothefuckup",
    "wibson",
    "Wicca",
    "WidescreenWallpaper",
    "wien",
    "WiggleButts",
    "wigglegrams",
    "WigglyAnimals",
    "wii",
    "WiiHacks",
    "WiiUHacks",
    "wildbeef",
    "wildhearthstone",
    "wildhockey",
    "Wildlands",
    "Wildlife",
    "wildlifephotography",
    "wildlypenis",
    "WildStar",
    "wince",
    "windows8",
    "windowshots",
    "WindowsMR",
    "windowsphone",
    "winemaking",
    "Winnipeg",
    "winnipegjets",
    "wisconsin",
    "Wishlist",
    "Witcher3",
    "WitchesVsPatriarchy",
    "WithoutATrace",
    "Wizard101",
    "wlw_irl",
    "wma",
    "WoahTube",
    "WoahTunes",
    "wolves",
    "WolvesWithWatermelons",
    "women",
    "womensstreetwear",
    "wonderdraft",
    "WonderTrade",
    "Woodcarving",
    "Woodworkingplans",
    "Woodworkingvideos",
    "woofbarkwoof",
    "words",
    "work",
    "workaholics",
    "Workbenches",
    "workflow",
    "workout",
    "Workspaces",
    "worldofpvp",
    "worldofwarcraft",
    "worldwarzthegame",
    "worldwhisky",
    "WorseEveryLoop",
    "WOSH",
    "WoT",
    "wowguilds",
    "wownoob",
    "WowUI",
    "WQHD_Wallpaper",
    "Wrangler",
    "Wrasslin",
    "wrestling",
    "write",
    "writers",
    "WritersGroup",
    "WRX",
    "wtfamazon",
    "wtfart",
    "wtfdidijustread",
    "WTFwish",
    "ww2",
    "wwe_network",
    "WWEGames",
    "WWEstreams",
    "wwesupercard",
    "wwi",
    "WWIIplanes",
    "WWOOF",
    "wyzecam",
    "xbmc",
    "xboxinsiders",
    "XboxOneGamers",
    "XCOM2",
    "xDACplatform",
    "Xenoblade_Chronicles",
    "XFiles",
    "xfl",
    "xkcdcomic",
    "xmen",
    "xposed",
    "xqcow",
    "XRayPorn",
    "XRP",
    "xTrill",
    "XWingTMG",
    "xXRealGamerzXx",
    "Yahaha_IRL",
    "yahooanswers",
    "yakuzagames",
    "YAlit",
    "yandere_simulator",
    "YangForPresidentHQ",
    "yankees",
    "YarnAddicts",
    "YasuoMains",
    "yescompanionimbecil",
    "YMS",
    "YogaWorkouts",
    "Yosemite",
    "youdontmattergiveup",
    "YouEnterADungeon",
    "youngjustice",
    "Youniqueamua",
    "YouOnLifetime",
    "yourmomshousepodcast",
    "YouTube_startups",
    "youtubecomments",
    "YoutubeCompendium",
    "YouTubeGamers",
    "youtubegaming",
    "youtubesyllables",
    "youtubetv",
    "YovannaVentura",
    "YuB",
    "YUROP",
    "yvonnestrahovski"
]
"""

if __name__ == "__main__":
    data = dict()
    submissions: List[Submission] = []
    for subreddit_name in default_reddit_subreddits:
        subreddit: Subreddit = rwrapper.reddit.subreddit(subreddit_name)
        submissions.extend(list(subreddit.controversial("all")))
    length = len(submissions)
    studies: List[float] = []
    for amount in amounts:
        if(length >= amount):
            print(f"Analizando {amount} registros...")
            start = time.time()
            analysis = rwrapper.analyzer.analyze_submissions(submissions[0: amount], True)[0]
            end = time.time()
            elapsed = end - start
            danalysis = list(analysis.toDict().values())
            danalysis.append(elapsed)
            studies.append(danalysis)
    print("Análisis Finalizado")
    columns = list(analysis.toDict().keys())
    columns.append("Duracion")
    df = pd.DataFrame(studies, index=amounts, columns=columns)
    filename = f"test-{str(uuid4()).split('-')[0]}.xlsx"
    df.to_excel(filename)
    print(f"Archivo {filename} creado con éxito!")
            
            

