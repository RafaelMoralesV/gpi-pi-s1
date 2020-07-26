import time
import pickle
from typing import List, Dict, Union
from dictionary import get_dictionary
from models.twitter import TwitterData, TwitterStreamer, TwitterClient, TwitterAnalyzer

dict_path = "./data/diccionario.json"
dictionary = get_dictionary(dict_path)
twitter_client = TwitterClient()
twitter_analyzer = TwitterAnalyzer(dictionary)

hashtags = [
    '30secondmom',
    'AllStars5',
    'AmericasGreatestMistake',
    'BLM',
    'COVID19',
    'Cubs',
    'DragRace',
    'ForTheH',
    'GoCubsGo',
    'MLB',
    'MLBOpeningDay',
    'Mariners',
    'NationalTequilaDay',
    'OpeningDay',
    'STLCards',
    'SmackDown',
    'TeamShea',
    'adventure',
    'aflswanshawks',
    'againstbullying',
    'allstar5',
    'allstars5',
    'amazing',
    'americasgreatestmistake',
    'android',
    'aprilfollsday',
    'art',
    'asimforthewin',
    'auspol',
    'australia',
    'baby',
    'backwheniwasakid',
    'bangbangcon',
    'bbcqt',
    'bcpoli',
    'beach',
    'beautiful',
    'beauty',
    'believe',
    'bestoftheday',
    'bigdata',
    'black',
    'blackandwhite',
    'blackhistorymonth',
    'blacklivesmatter',
    'blackswan',
    'blm',
    'blockchain',
    'bloods2020',
    'blownoff',
    'blue',
    'bornbravevbus',
    'btswins10s',
    'bullying',
    'bullyinghurts',
    'business',
    'canada',
    'cat',
    'caturday',
    'change',
    'chartbustersid',
    'chickennoodlesoup',
    'childtrafficking',
    'christmas',
    'cleaneating',
    'cloud',
    'coffe',
    'competition',
    'contest',
    'cooking',
    'cool',
    'crypto',
    'cute',
    'cyber',
    'dancemoms',
    'dateline',
    'delicious',
    'demifact',
    'design',
    'device',
    'dog',
    'dontdothisaftersex',
    'drawing',
    'eatclean',
    'eathealthy',
    'electronic',
    'engineering',
    'england',
    'equality',
    'ethereum',
    'eventful',
    'f4f',
    'family',
    'fashion',
    'fashionblogger',
    'fashioninspo',
    'fashionista',
    'fit',
    'fitfam',
    'fitfood',
    'fitlife',
    'fitness',
    'fitnessaddict',
    'fitnessmotivation',
    'fitquote',
    'fitspo',
    'flashbackfriday',
    'florida',
    'flowers',
    'folklore',
    'follow',
    'follow4follow',
    'followback',
    'followforfollow',
    'followme',
    'food',
    'foodcoma',
    'foodgasm',
    'foodie',
    'foodpic',
    'foodporn',
    'foodstagram',
    'forthea',
    'fortheh',
    'freecodefridaycontest',
    'fridaymorning',
    'friend',
    'friends',
    'friyay',
    'fun',
    'funny',
    'fursuitfriday',
    'gadget',
    'getalife',
    'getaway',
    'getfit',
    'gethealthy',
    'girl',
    'girls',
    'girlswholift',
    'giveaway',
    'grammys',
    'growup',
    'gym',
    'gymlife',
    'hair',
    'handmade',
    'happy',
    'happyeaster',
    'harassment',
    'harper',
    'healthinsurance',
    'healthtalk',
    'healthy',
    'healthylife',
    'highschoolmemories',
    'home',
    'honestyhour',
    'hope',
    'hot',
    'howimdoing',
    'howyoulikethat',
    'hypocrites',
    'iamup',
    'icantstandpeople',
    'ico',
    'ifitwereuptome',
    'igers',
    'igotnorespectforyou',
    'igtravel',
    'ihopesomeday',
    'ilovetravel',
    'inelementaryschool',
    'influencermarketing',
    'innovation',
    'instacool',
    'instadaily',
    'instafashion',
    'instafollow',
    'instafood',
    'instagood',
    'instagram',
    'instalike',
    'instalove',
    'instamood',
    'instapic',
    'instatech',
    'instatravel',
    'instavacation',
    'internationalwomensday',
    'ios',
    'iphone',
    'iphoneonly',
    'itdoesnotmakeyoucool',
    'itgetsbetter',
    'iwanttopunchpeoplewho',
    'iwillnevverunderstand',
    'justsayin',
    'kindle',
    'kissingbooth2',
    'l4l',
    'liamfact',
    'liamfacts',
    'life',
    'lifestyle',
    'lightningstrikes',
    'like4like',
    'likeforlike',
    'lol',
    'london',
    'lookbook',
    'love',
    'loveisallweneed',
    'lufc',
    'maga',
    'makeachange',
    'makeup',
    'makeupaddict',
    'me',
    'meanie',
    'medbikini',
    'medicaid',
    'meetthepress',
    'melbourne',
    'mensfashion',
    'mental',
    'mentalhealth',
    'menwhocook',
    'merrychristmas',
    'metoo',
    'miami',
    'middlefingerup',
    'middleschoolmemories',
    'mikebully',
    'mittromney',
    'mobile',
    'model',
    'mondaymotivation',
    'morningrushatl',
    'motivation',
    'music',
    'my',
    'mychance',
    'mytravelgram',
    'nationaltequiladay',
    'nature',
    'neverwouldiever',
    'newbedon',
    'newprofilepic',
    'news',
    'night',
    'noexcuses',
    'nofilter',
    'nom',
    'nomorebullies',
    'notalone',
    'notfair',
    'nutrition',
    'nyc',
    'obamagate',
    'obese',
    'olympics',
    'ootd',
    'openingday2020',
    'operationpurplesky',
    'opioid',
    'oscars',
    'overth',
    'party',
    'peace',
    'peoplewhowerebulliedbutnowsuccessful',
    'photo',
    'photography',
    'photooftheday',
    'pickone',
    'picoftheday',
    'pink',
    'pinkshirtday',
    'pizza',
    'politics',
    'portland',
    'portlandprotest',
    'powertrip',
    'pressforprogress',
    'pretty',
    'puppy',
    'realtalk',
    'redv',
    'repost',
    'ripericmonster',
    'roadtrip',
    'rootedinoakland',
    'running',
    'sadtweet',
    'safety',
    'satchat',
    'saturdaymorning',
    'savealife',
    'schoolmemories',
    'schools',
    'science',
    'sea',
    'secondaryschoolconfessions',
    'selfie',
    'shinedown',
    'shinedown2012',
    'shoplocal',
    'sky',
    'smackdown',
    'smile',
    'snack',
    'socialmedia',
    'soda',
    'song',
    'sorrynotsorry',
    'sosad',
    'soundcloud',
    'soxmath',
    'spiritday',
    'standup',
    'startups',
    'staysafe',
    'stfu',
    'stopbullying',
    'stophate',
    'stoprush',
    'stopthehate',
    'streetstyle',
    'streetwear',
    'style',
    'stylegram',
    'styleoftheday',
    'stylish',
    'subtweet',
    'summer',
    'sun',
    'sunset',
    'support',
    'sushi',
    'swag',
    'sweat',
    'sweet',
    'swiftfact',
    'sydney',
    'tagsforlikes',
    'takeastand',
    'tasty',
    'tbt',
    'teach',
    'teaparty',
    'tech',
    'technews',
    'technology',
    'techtrends',
    'tflers',
    'thankful',
    'thanksbatfleck',
    'thataintcool',
    'themusicvideo',
    'theoutrunners',
    'theworstendingever',
    'thingsthatbotherme',
    'thingsthatgetmeupset',
    'todayiwore',
    'topsecretreidfact',
    'toronto',
    'tourism',
    'tourist',
    'trainhard',
    'travel',
    'travelblogger',
    'traveldeeper',
    'traveler',
    'travelgram',
    'traveling',
    'travelphotography',
    'traveltuesday',
    'trend',
    'truestory',
    'tuesdaymotivation',
    'tvo',
    'twograves',
    'upup',
    'usa',
    'vacation',
    'vancouver',
    'victim',
    'video',
    'vintage',
    'vsco',
    'vscocam',
    'wakeup11',
    'wallofmoms',
    'wanderer',
    'wanderlust',
    'wcw',
    'webstagram',
    'wedding',
    'weekend',
    'weliveinagenerationwhere',
    'whatdoyouthinkitsokayto',
    'whatif',
    'whatwereyouthinking',
    'wheniwasyounger',
    'winningsid',
    'winter',
    'womenshistorymonth',
    'work',
    'workout',
    'workplace',
    'xatiada',
    'yoga',
    'youtube',
    'yummy',
]

if __name__ == "__main__":
    tweets: List[Dict[str, Union[str, int]]] = []
    stamp: str = time.strftime("%H:%M")
    print(f"[{stamp}] Consultando entradas de twitter")
    for hashtag in hashtags:
        stamp = time.strftime("%H:%M")
        print(f"[{stamp}] Consultando #{hashtag}")
        tws = twitter_client.get_hashtag_tweets_to_analyze("#" + hashtag)
        print(len(tws))
        tweets.extend(tws)
    stamp = time.strftime("%H:%M")
    print(f"[{stamp}] Guardando {len(tweets)} Entradas...")
    with open("data/tweets.dat", "wb") as twfile:
        print(len(tweets))
        pickle.dump(tweets, twfile)
        print(f"[{stamp}] Archivo creado con éxito")
