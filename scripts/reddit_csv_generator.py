import csv
import praw

reddit = praw.Reddit(client_id="AUs7RM1sxg8Itg", user_agent="my user agent", client_secret="NVkkQtixo7aMWnDjGqi8fCmUP_g")

def record_subreddit(writer, subreddit_name: str, limit: int):
    subreddit = reddit.subreddit(subreddit_name)
    for sub in reddit.subreddit(subreddit_name).hot(limit=limit):
        if(sub.author):
            writer.writerow([sub.id, sub.title, sub.author.id, sub.author.name, sub.score, sub.upvote_ratio, subreddit.id, subreddit.title, str(int(sub.created_utc))])
        else:
            writer.writerow([sub.id, sub.title, "", "", sub.score, sub.upvote_ratio, subreddit.id, subreddit.title, str(int(sub.created_utc))])

with open('reddit.csv', mode='w') as reddit_csv:
    fieldnames = ['id_submission', 'title', 'id_author', 'author', 'score', 'upvote_ratio', 'id_subreddit' ,'subreddit', 'created_utc']
    file_writer = csv.writer(reddit_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(fieldnames)
    record_subreddit(file_writer, "chile", 300)
    record_subreddit(file_writer, "ChileArte", 40)
    record_subreddit(file_writer, "Chilefit", 30)
    print("Registros guardados!")