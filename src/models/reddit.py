from models.base import Analysis, BaseAnalyzer, BaseAPIWrapper
import praw
from praw.models import Redditor, Comment


class RedditAnalyzer(BaseAnalyzer):

    def analyze_user(self, redditor: Redditor):
        liderazgo = self.get_liderazgo(redditor)
        asertividad = self.get_asertividad(redditor)
        analysis = Analysis(liderazgo=liderazgo, asertividad=asertividad)
        return analysis


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


class RedditWrapper(BaseAPIWrapper):

    analyzer : RedditAnalyzer
    reddit : praw.Reddit

    def __init__(self, reddit : praw.Reddit ,analyzer: RedditAnalyzer):
        self.analyzer = analyzer
        self.reddit = reddit

    def analyze_user_by_id(self, user_id: str):
        redditor = self.reddit.redditor(user_id)
        return self.analyzer.analyze_user(redditor)
    

