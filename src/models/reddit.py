from models.base import Analysis, BaseAnalyzer, BaseAPIWrapper
import praw
from praw.models import Redditor, Comment, Subreddit, Submission
from textblob import TextBlob
from statistics import mean
from typing import List

class RedditAnalyzer(BaseAnalyzer):

    def analyze_user(self, redditor: Redditor):
        optimismo = self.get_optimismo_by_user(redditor)
        violencia = self.get_violencia_by_user(redditor)
        return Analysis(optimismo=optimismo, violencia=violencia)

    def analyze_subreddit(self, subreddit: Subreddit):
        optimismo = self.get_optimismo_by_subreddit(subreddit)
        violencia = self.get_violencia_by_user(subreddit)
        return Analysis(optimismo=optimismo, violencia=violencia)

    def get_liderazgo(self, redditor: Redditor):
        matches = 0
        for comment in redditor.comments.controversial():
            comment : Comment
            matches += self.match_factor_dict(comment.body, 'liderazgo')
        return matches
    
    def get_asertividad(self, redditor: Redditor):
        matches = 0
        for comment in redditor.comments.controversial():
            comment : Comment
            matches += self.match_factor_dict(comment.body, 'asertividad')
        return matches


    # Optimismo

    def get_optimismo_by_subreddit(self, subreddit: Subreddit):
        return self.get_optimismo_by_list([(comment.body) for comment in subreddit.comments(limit=20)])

    def get_optimismo_by_user(self, redditor: Redditor):
        return self.get_optimismo_by_list([(comment.body) for comment in redditor.comments(limit=20)])

    def get_optimismo_by_list(self, strlist: List[str]):
        resultset = [self.get_optimismo_by_text(text) for text in strlist]
        score = mean(resultset)
        return score*100 if score > 0 else 0

    def get_optimismo_by_text(self, text: str) -> float:
        return TextBlob(text).polarity
    
    
    # Violencia

    def get_violencia_by_user(self, redditor: Redditor):
        return self.get_violencia_by_list([(comment.body) for comment in redditor.comments(limit=20)])

    def get_violencia_by_list(self, redditor: Redditor):
        return self.get_violencia_by_list([(comment.body) for comment in redditor.comments(limit=20)])

    def get_violencia_by_list(self, strlist: List[str]):
        resultset = [self.get_violencia_by_text(text) for text in strlist]
        score = mean(resultset)
        return score*100 if score > 0 else 0

    def get_violencia_by_text(self, text: str) -> float:
        return self.get_optimismo_by_text(text)*-1

    def get_empatia_by_user(self, redditor: Redditor):
        return self.get_empatia_by_list([sub for sub in redditor.submissions.top("all")])

    def get_empatia_by_list(self, sublist: List[Submission]):
        resultset = [self.get_empatia_by_sub(sub) for sub in sublist]
        score = mean(resultset)
        return score, sublist, resultset

    def get_empatia_by_sub(self, sub:Submission):
        if(sub.selftext):
            return self.get_empatia_by_text(sub.selftext)*0.7 + self.get_empatia_by_text(sub.title)*0.3
        else:
            return self.get_empatia_by_text(sub.title)

    def get_empatia_by_text(self,text: str):
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subj = blob.subjectivity
        matches = self.match_factor_dict(text, 'empatia')
        match_score = matches*10 if matches <= 5 else 10
        score = pol*80+subj*10+match_score
        print(text)
        print(f"pol={pol} subj={subj} matches={self.match_factor_dict(text, 'empatia')}")
        print(score)
        print("\n")
        return score



class RedditWrapper(BaseAPIWrapper):

    analyzer : RedditAnalyzer
    reddit : praw.Reddit

    def __init__(self, reddit : praw.Reddit ,analyzer: RedditAnalyzer):
        self.analyzer = analyzer
        self.reddit = reddit

    def analyze_user_by_id(self, user_id: str):
        redditor = self.reddit.redditor(user_id)
        return self.analyzer.analyze_user(redditor)
    
    def analyze_subreddit_by_id(self, subreddit_id: str):
        subreddit = self.reddit.subreddit(subreddit_id)
        return self.analyzer.analyze_subreddit(subreddit)
    

