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

amounts = [5, 10, 50, 100, 200]

default_reddit_subreddits = ["golang", "Futurology", "MemeEconomy"]

"""
# Descomentar después de prueba inicial (cantidad máxima estimada de submissions: 51000)
amounts = [5, 10, 50, 100, 500, 1000, 2500, 5000, 10000, 50000]

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
    "wholesomefortnite",
    "wholesomejojo",
    "Wholesomenosleep",
    "wholesomeouija",
    "wholesomeoverwatch",
    "wholesomepranks",
    "wholesomeprequelmemes",
    "wholesomevandalism",
    "whoosh",
    "whoselineisitanyway",
    "whothefuckup",
    "wibson",
    "Wicca",
    "WidescreenWallpaper",
    "wien",
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
    "YuB",
    "YUROP",
    "yvonnestrahovski",
    "painting",
    "Paladins",
    "Paleo",
    "PandR",
    "panelshow",
    "PanPorn",
    "papertowns",
    "paradoxplaza",
    "Paranormal",
    "Pareidolia",
    "Parenting",
    "parrots",
    "PartyParrot",
    "Pathfinder_RPG",
    "pathofexile",
    "patientgamers",
    "Patriots",
    "paydaytheheist",
    "pcgaming",
    "pcmasterrace",
    "pennystocks",
    "penpals",
    "PeopleBeingJerks",
    "PeopleFuckingDying",
    "peopleofwalmart",
    "Perfectfit",
    "perfectloops",
    "perfectlycutscreams",
    "PerfectTiming",
    "Permaculture",
    "Persona5",
    "personalfinance",
    "PersonalFinanceCanada",
    "Pets",
    "PetTheDamnDog",
    "pettyrevenge",
    "pewdiepie",
    "PewdiepieSubmissions",
    "pharmacy",
    "philadelphia",
    "Philippines",
    "philosophy",
    "PhilosophyofScience",
    "phoenix",
    "PhonesAreBad",
    "photocritique",
    "photography",
    "photoshop",
    "photoshopbattles",
    "PhotoshopRequest",
    "PHP",
    "Physics",
    "physicsgifs",
    "piano",
    "pic",
    "pickuplines",
    "picrequests",
    "pics",
    "piercing",
    "Pikabu",
    "pinkfloyd",
    "Piracy",
    "pitbulls",
    "pittsburgh",
    "PixelArt",
    "Pizza",
    "place",
    "Planetside",
    "PlantedTank",
    "playark",
    "PlayItAgainSam",
    "playrust",
    "playstation",
    "PlayStationPlus",
    "PleX",
    "podcasts",
    "Poetry",
    "pokemon",
    "pokemongo",
    "PokemonLetsGo",
    "pokemontrades",
    "poker",
    "polandball",
    "Political_Revolution",
    "PoliticalDiscussion",
    "PoliticalHumor",
    "politics",
    "Polska",
    "polyamory",
    "popheads",
    "popping",
    "poppunkers",
    "pornfree",
    "PornhubComments",
    "Porsche",
    "Portal",
    "Portland",
    "portugal",
    "PostHardcore",
    "postprocessing",
    "povertyfinance",
    "powerlifting",
    "PowerShell",
    "powerwashingporn",
    "PraiseTheCameraMan",
    "Prematurecelebration",
    "premed",
    "PremierLeague",
    "preppers",
    "PrequelMemes",
    "printSF",
    "Prisonwallet",
    "privacy",
    "productivity",
    "ProductPorn",
    "progmetal",
    "ProgrammerHumor",
    "programming",
    "programminghorror",
    "progressive",
    "progresspics",
    "progun",
    "projectcar",
    "PropagandaPosters",
    "ProperAnimalNames",
    "ProRevenge",
    "ProtectAndServe",
    "PS3",
    "PS4",
    "PS4Deals",
    "PSVR",
    "Psychic",
    "PsychologicalTricks",
    "psychology",
    "Psychonaut",
    "PUBATTLEGROUNDS",
    "PUBG",
    "PUBGMobile",
    "PUBGXboxOne",
    "PublicFreakout",
    "pugs",
    "punchablefaces",
    "punk",
    "Punny",
    "PunPatrol",
    "puns",
    "puppies",
    "puppy101",
    "PuppySmiles",
    "pureasoiaf",
    "Purrito",
    "PussyPass",
    "pussypassdenied",
    "Pyongyang",
    "pyrocynical",
    "Python",
    "IAmA",
    "iamatotalpieceofshit",
    "iamverybadass",
    "iamveryrandom",
    "iamverysmart",
    "IASIP",
    "ICanDrawThat",
    "ich_iel",
    "icocrypto",
    "IdiotsFightingThings",
    "IdiotsInCars",
    "IdiotsNearlyDying",
    "IDontWorkHereLady",
    "Idubbbz",
    "ifyoulikeblank",
    "ihadastroke",
    "ihavereddit",
    "ihavesex",
    "iiiiiiitttttttttttt",
    "ik_ihe",
    "ilikthebred",
    "IllegalLifeProTips",
    "illusionporn",
    "Illustration",
    "im14andthisisdeep",
    "Images",
    "ImaginaryBehemoths",
    "ImaginaryCharacters",
    "ImaginaryCityscapes",
    "ImaginaryLandscapes",
    "ImaginaryLeviathans",
    "imaginarymaps",
    "ImaginaryMindscapes",
    "ImaginaryMonsters",
    "ImaginarySliceOfLife",
    "ImaginaryTechnology",
    "ImaginaryWesteros",
    "Impeach_Trump",
    "imsorryjon",
    "imveryedgy",
    "InclusiveOr",
    "Incorgnito",
    "incremental_games",
    "india",
    "IndianFood",
    "indianpeoplefacebook",
    "IndieGaming",
    "indieheads",
    "Indiemakeupandmore",
    "IndoorGarden",
    "INEEEEDIT",
    "Infographics",
    "infp",
    "InfrastructurePorn",
    "insaneparents",
    "insanepeoplefacebook",
    "InsightfulQuestions",
    "Instagram",
    "Instagramreality",
    "instant_regret",
    "instantbarbarians",
    "instantkarma",
    "instantpot",
    "Instantregret",
    "intel",
    "InterdimensionalCable",
    "interestingasfuck",
    "InteriorDesign",
    "intermittentfasting",
    "InternetIsBeautiful",
    "internetparents",
    "InternetStars",
    "inthenews",
    "inthesoulstone",
    "intj",
    "INTP",
    "intresseklubben",
    "introvert",
    "intrusivethoughts",
    "investing",
    "ios",
    "iosgaming",
    "iOSProgramming",
    "iOSthemes",
    "Iota",
    "ipad",
    "iphone",
    "ireland",
    "IRLEasterEggs",
    "IRLgirls",
    "irlsmurfing",
    "IsItBullshit",
    "islam",
    "IsolatedVocals",
    "IsTodayFridayThe13th",
    "italy",
    "ITCareerQuestions",
    "ItemShop",
    "itookapicture",
    "itsaunixsystem",
    "iWallpaper",
    "ableton",
    "ABoringDystopia",
    "ABraThatFits",
    "absolutelynotme_irl",
    "absolutelynotmeirl",
    "AbsoluteUnits",
    "AccidentalComedy",
    "AccidentalRacism",
    "AccidentalRenaissance",
    "accidentalswastika",
    "AccidentalWesAnderson",
    "Accounting",
    "ActLikeYouBelong",
    "actuallesbians",
    "Addons4Kodi",
    "ADHD",
    "AdrenalinePorn",
    "AdvancedFitness",
    "adventuretime",
    "advertising",
    "Advice",
    "AdviceAnimals",
    "afkarena",
    "agedlikemilk",
    "ainbow",
    "AionNetwork",
]
"""

if __name__ == "__main__":
    submissions: List[Submission] = []
    print("Consultando entradas de reddit")
    for subreddit_name in default_reddit_subreddits:
        print(f"Consultando {subreddit_name}")
        subreddit: Subreddit = rwrapper.reddit.subreddit(subreddit_name)
        try:
            submissions.extend(list(subreddit.controversial("all")))
        except:
            print("Error: " + subreddit_name)
    print("Iniciando análisis...")
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
    filename = f"reddit-test-{str(uuid4()).split('-')[0]}.xlsx"
    df.to_excel(filename)
    print(f"Archivo {filename} creado con éxito!")
            

