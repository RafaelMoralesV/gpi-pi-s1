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
        return self.analyze_submissions(submissions, True)
    
    def analyze_submissions(self, sublist: List[Submission], is_subreddit: bool = False) -> (Analysis, List[Submission]):
        if is_subreddit:
            percepcion = self.switch_factor_grouped(sublist, 'percepcion')
            colaboracion = self.switch_factor_grouped(sublist, 'colaboracion')
        else:
            percepcion = self.switch_factor(sublist, 'percepcion')
            colaboracion = self.switch_factor(sublist, 'colaboracion')

        empatia = self.switch_factor(sublist, 'empatia')
        autoconciencia_emocional = self.switch_factor(sublist, 'autoconciencia')
        autoestima = self.switch_factor(sublist, 'autoestima')
        return Analysis(
            empatia=empatia, colaboracion=colaboracion, percepcion=percepcion, 
            autoconciencia_emocional=autoconciencia_emocional, autoestima=autoestima), sublist

    def analyze_submission(self, submission: Submission) -> Analysis:
        empatia = self.switch_factor(submission, 'empatia')
        colaboracion = self.switch_factor(submission, 'colaboracion')
        percepcion = self.switch_factor(submission, 'percepcion')
        autoconciencia_emocional = self.switch_factor(submission, 'autoconciencia')
        autoestima = self.switch_factor(submission, 'autoestima')
        return Analysis(
            empatia=empatia, colaboracion=colaboracion, percepcion=percepcion, 
            autoconciencia_emocional=autoconciencia_emocional, autoestima=autoestima)


    # Autoconciencia emocional

    def get_autoconciencia_by_sub(self, sub: Submission):
        if(sub.selftext):
            return self.get_autoconciencia_by_text(sub.selftext)*0.7 + self.get_autoconciencia_by_text(sub.title)*0.3
        else:
            return self.get_autoconciencia_by_text(sub.title)      

    def get_autoconciencia_by_text(self, text: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'autoconciencia_emocional')
        match_score = matches*6 if matches <= 5 else 30
        score = subj*70 + match_score
        return score
    
    # Autoestima

    def get_autoestima_by_sub(self, sub: Submission):
        if(sub.selftext):
            return self.get_autoestima_by_text(sub.selftext)*0.7 + self.get_autoestima_by_text(sub.title)*0.3
        else:
            return self.get_autoestima_by_text(sub.title)

    def get_autoestima_by_text(self, text: str):
        blob = TextBlob(text)
        subj = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'autoestima')
        match_score = matches * 6 if matches <= 10 else 60
        score = subj*40 + match_score
        return score

    # Colaboración y Cooperación

    def get_colaboracion_by_grouped_sub(self, sub:Submission):
        votes_score = sub.upvote_ratio
        if(sub.selftext):
            return self.get_colaboracion_by_text(sub.selftext, votes_score, 10)*0.7 + self.get_colaboracion_by_text(sub.title, votes_score, 10)*0.3
        else:
            return self.get_colaboracion_by_text(sub.title, votes_score,10)

    def get_colaboracion_by_sub(self, sub: Submission) -> float:
        votes_score = sub.upvote_ratio
        if(sub.selftext):
            return self.get_colaboracion_by_text(sub.selftext, votes_score,5)*0.7 + self.get_colaboracion_by_text(sub.title, votes_score,5)*0.3
        else:
            return self.get_colaboracion_by_text(sub.title, votes_score,5)

    def get_colaboracion_by_text(self, text: str, votes_score: float, word_limit: int) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(text.lower(), 'colaboracion_cooperacion')
        match_score = matches*(50/word_limit) if matches <= word_limit else 50
        score = pol*20 + votes_score*30+match_score
        return score

    # Empatia
    
    def get_empatia_by_sub(self, sub:Submission) -> float:
        votes_score = sub.upvote_ratio
        if(sub.selftext):
            return self.get_empatia_by_text(sub.selftext, votes_score)*0.7 + self.get_empatia_by_text(sub.title, votes_score)*0.3
        else:
            return self.get_empatia_by_text(sub.title, votes_score)

    def get_empatia_by_text(self,text: str, votes_score: float) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subj = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'empatia')
        match_score = matches*10 if matches <= 5 else 50
        score = pol*20+subj*10+match_score+votes_score*20
        return score

    # Liderazgo

    def get_liderazgo_by_sub(self, sub: Submission):
        votes_score = sub.upvote_ratio
        if(sub.selftext):
            return self.get_liderazgo_by_text(sub.selftext, votes_score)*0.7 + self.get_liderazgo_by_text(sub.title, votes_score)*0.3
        else:
            return self.get_liderazgo_by_text(sub.title, votes_score)

    def get_liderazgo_by_text(self, text:str, votes_score: float) -> float:
        matches = self.match_factor_dict(text.lower(), 'liderazgo')
        match_score = matches*4 if matches <= 10 else 40
        score = votes_score*60+match_score
        return score

    # Percepción y comprension emocional

    def get_percepcion_by_grouped_sub(self, sub:Submission):
        if(sub.selftext):
            return self.get_percepcion_by_text(sub.selftext, 10, 20, 30)*0.7 + self.get_percepcion_by_text(sub.title, 10, 20, 30)*0.3
        else:
            return self.get_percepcion_by_text(sub.title, 10, 20, 30)

    def get_percepcion_by_sub(self, sub: Submission) -> float:
        if(sub.selftext):
            return self.get_percepcion_by_text(sub.selftext, 5, 30, 20)*0.7 + self.get_percepcion_by_text(sub.title, 5, 30, 20)*0.3
        else:
            return self.get_percepcion_by_text(sub.title, 5,30, 20)

    def get_percepcion_by_text(self, text: str, word_limit: int, pol_max_score:int, subj_max_score: int) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'percepcion_comprension_emocional')
        match_score = matches*(50/word_limit) if matches <= word_limit else 50
        score = pol*pol_max_score + subjectivity*subj_max_score+match_score
        return score

    def switch_factor(self, sublist: Union[Submission, List[Submission]], factor: str) -> float:
        factor_method = f"get_{factor}_by_sub"    
        method = getattr(self, factor_method)
        if type(sublist) != list:
            return method(sublist)
        resultset = [method(sub) for sub in sublist]
        score = mean(resultset)
        print(factor_method)
        return score
    
    def switch_factor_grouped(self, sublist: Union[Submission, List[Submission]], factor: str) -> float:
        factor_method = f"get_{factor}_by_grouped_sub"    
        method = getattr(self, factor_method)
        if type(sublist) != list:
            return method(sublist)
        resultset = [method(sub) for sub in sublist]
        score = mean(resultset)
        print(factor_method)
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
    

