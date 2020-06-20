from models.base import Analysis, BaseAnalyzer, BaseAPIWrapper
import praw
from praw.models import Redditor, Comment, Subreddit, Submission
from textblob import TextBlob
from statistics import mean
from typing import List, Union

class RedditAnalyzer(BaseAnalyzer):

    def analyze_user(self, redditor: Redditor) -> (Analysis, List[Submission]):
        submissions = list(redditor.submissions.top("all"))
        return self.analyze_submissions(submissions)

    def analyze_subreddit(self, subreddit: Subreddit):
        submissions = list(subreddit.hot())
        return self.analyze_submissions(submissions)
    
    def analyze_submissions(self, sublist: List[Submission]) -> (Analysis, List[Submission]):
        empatia = self.switch_factor(sublist, 'empatia')
        colaboracion = self.switch_factor(sublist, 'colaboracion')
        percepcion = self.switch_factor(sublist, 'percepcion')
        return Analysis(empatia=empatia, colaboracion=colaboracion, percepcion=percepcion), sublist

    def analyze_submission(self, submission: Submission) -> Analysis:
        empatia = self.switch_factor(submission, 'empatia')
        colaboracion = self.switch_factor(submission, 'colaboracion')
        percepcion = self.switch_factor(submission, 'percepcion')
        return Analysis(empatia=empatia, colaboracion=colaboracion, percepcion=percepcion)

    # Colaboración y Cooperación

    def get_colaboracion_by_sub(self, sub: Submission) -> float:
        votes_score = sub.upvote_ratio
        if(sub.selftext):
            return self.get_colaboracion_by_text(sub.selftext.lower(), votes_score)*0.7 + self.get_colaboracion_by_text(sub.title.lower(), votes_score)*0.3
        else:
            return self.get_colaboracion_by_text(sub.title.lower(), votes_score)

    def get_colaboracion_by_text(self, text: str, votes_score: float) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(text, 'colaboracion_cooperacion')
        match_score = matches*10 if matches <= 5 else 50
        score = pol*20 + votes_score*30+match_score
        return score

    # Empatia

    def get_empatia_by_sub(self, sub:Submission) -> float:
        votes_score = sub.upvote_ratio
        if(sub.selftext):
            return self.get_empatia_by_text(sub.selftext.lower(), votes_score)*0.7 + self.get_empatia_by_text(sub.title.lower(), votes_score)*0.3
        else:
            return self.get_empatia_by_text(sub.title.lower(), votes_score)

    def get_empatia_by_text(self,text: str, votes_score: float) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subj = blob.subjectivity
        matches = self.match_factor_dict(text, 'empatia')
        match_score = matches*10 if matches <= 5 else 50
        score = pol*20+subj*10+match_score+votes_score*20
        return score

    # Percepción y comprension emocional

    def get_percepcion_by_sub(self, sub: Submission) -> float:
        if(sub.selftext):
            return self.get_percepcion_by_text(sub.selftext.lower())*0.7 + self.get_percepcion_by_text(sub.title.lower())*0.3
        else:
            return self.get_percepcion_by_text(sub.title.lower())

    def get_percepcion_by_text(self, text: str) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text, 'percepcion_comprension_emocional')
        match_score = matches*10 if matches <= 5 else 50
        score = pol*30 + subjectivity*20+match_score
        return score

    def switch_factor(self, sublist: Union[Submission, List[Submission]], factor: str) -> float:
        factor_method = f"get_{factor}_by_sub"    
        method = getattr(self, factor_method)
        if type(sublist) != list:
            return method(sublist)
        resultset = [method(sub) for sub in sublist]
        score = mean(resultset)
        return score

class RedditWrapper(BaseAPIWrapper):

    analyzer : RedditAnalyzer
    reddit : praw.Reddit

    def __init__(self, reddit : praw.Reddit ,analyzer: RedditAnalyzer):
        self.analyzer = analyzer
        self.reddit = reddit

    def analyze_user_by_id(self, user_id: str) -> dict:
        redditor = self.reddit.redditor(user_id)
        analysis, submissions = self.analyzer.analyze_user(redditor)
        subs = []
        for sub in submissions:
            subs.append({
                "id" : sub.id,
                "name": sub.title,
                "n_comments" : sub.num_comments,
                "text" : sub.selftext
            })
        user_data = {
            "analysis" : analysis.toDict(),
            "icon_img" : redditor.icon_img,
            "id" : redditor.id,
            "name" : redditor.name,
            "submissions" : subs,
            "n_entries" : len(subs),
        }
        return user_data
    
    def analyze_subreddit_by_id(self, subreddit_id: str) -> dict:
        subreddit = self.reddit.subreddit(subreddit_id)
        analysis, submissions = self.analyzer.analyze_subreddit(subreddit)
        subs = []
        for sub in submissions:
            subs.append({
                "id" : sub.id,
                "name": sub.title,
                "n_comments" : sub.num_comments,
                "text" : sub.selftext
            })
        subreddit_data = {
            "analysis" : analysis.toDict(),
            "description": subreddit.public_description,
            "id" : subreddit.id,
            "name": subreddit.display_name,
            "subscribers" : subreddit.subscribers,
            "over18" : subreddit.over18,
            "n_entries" : len(subs),
            "submissions" : subs
        }
        return subreddit_data
    
    def analyze_submission_by_id(self, submission_id: str) -> Analysis:
        submission = self.reddit.submission(submission_id)
        return self.analyzer.analyze_submission(submission)
    

