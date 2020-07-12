import os
import praw
import json
from typing import List
from dotenv import load_dotenv
from dictionary import get_dictionary
from sheet import str_to_sheet
from .models.base import Analysis
from .models.reddit import RedditWrapper, RedditAnalyzer, Submission, Redditor

dictionary = get_dictionary(os.getenv("DICTIONARY_PATH"))
reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"), user_agent="my user agent", client_secret=os.getenv("REDDIT_CLIENT_SECRET"))
rwrapper = RedditWrapper(reddit, RedditAnalyzer(dictionary))
default_reddit_users = ["joeyisgoingto", "antikarma98", "Frustration", "Ginger_Lupus", "BreakfastforDinner"]
default_reddit_subreddits = ["golang", "Fitness", "lectures", "videogames", "politics", "Paranormal"]

if __name__ == "__main__":
    data = dict()
    data["users"] = dict()
    users: List[dict] = []
    entries: int = 0
    for name in default_reddit_users:
        print(f"Analyzing {name}...")
        user_data = rwrapper.analyze_user_by_id(name)
        entries += user_data["n_entries"]
        users.append(user_data)
    data["users"]["users"] = users
    data["users"]["n_entries"] = entries
    data["subreddits"] = dict()
    subreddits: List[Submission] = []
    entries: int = 0
    for name in default_reddit_subreddits:
        print(f"Analyzing {name}...")
        subreddit_data = rwrapper.analyze_subreddit_by_id(name)
        entries += len(subreddit_data["submissions"])
        subreddits.append(subreddit_data)
    data["subreddits"]["subreddits"] = subreddits
    data["subreddits"]["n_entries"] = entries
    with open("./data/reddit.json", "w") as rfile:
        json.dump(data, rfile)

