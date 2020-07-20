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
            conciencia = self.switch_factor_grouped(sublist, 'conciencia')
            tolerancia = self.switch_factor_grouped(sublist, 'tolerancia')
            comprension = self.switch_factor_grouped(sublist, 'comprension')
            asertividad = self.switch_factor_grouped(sublist, 'asertividad')
            desarrollo = self.switch_factor_grouped(sublist, 'desarrollo')
            liderazgo = self.switch_factor_grouped(sublist, 'liderazgo')
            manejo_conflictos = self.switch_factor_grouped(sublist, 'manejo_conflicto')
            violencia = self.switch_factor_grouped(sublist, 'violencia')
            relacion_social = self.switch_factor_grouped(sublist, 'relacion')
            optimismo = self.switch_factor_grouped(sublist, 'optimismo')
        else:
            percepcion = self.switch_factor(sublist, 'percepcion')
            colaboracion = self.switch_factor(sublist, 'colaboracion')
            conciencia = self.switch_factor(sublist, 'conciencia')
            tolerancia = self.switch_factor(sublist, 'tolerancia')
            comprension = self.switch_factor(sublist, 'comprension')
            asertividad = self.switch_factor(sublist, 'asertividad')
            desarrollo = self.switch_factor(sublist, 'desarrollo')
            liderazgo = self.switch_factor(sublist, 'liderazgo')
            manejo_conflictos = self.switch_factor(sublist, 'manejo_conflicto')
            violencia = self.switch_factor(sublist, 'violencia')
            relacion_social = self.switch_factor(sublist, 'relacion')
            optimismo = self.switch_factor(sublist, 'optimismo')
        empatia = self.switch_factor(sublist, 'empatia')
        autoconciencia_emocional = self.switch_factor(sublist, 'autoconciencia')
        autoestima = self.switch_factor(sublist, 'autoestima')
        motivacion = self.switch_factor(sublist, 'motivacion')
        return Analysis(
            empatia=empatia ,colaboracion_cooperacion=colaboracion, percepcion_comprension_emocional=percepcion, 
            autoconciencia_emocional=autoconciencia_emocional, autoestima=autoestima, 
            conciencia_critica = conciencia, tolerancia_frustracion=tolerancia,
            motivacion_logro = motivacion, comprension_organizativa=comprension,asertividad=asertividad,
            desarrollo_relaciones=desarrollo, liderazgo=liderazgo, manejo_conflictos=manejo_conflictos,
            relacion_social=relacion_social, optimismo=optimismo, violencia=violencia), sublist

    def analyze_submission(self, submission: Submission) -> Analysis:
        empatia = self.switch_factor(submission, 'empatia')
        colaboracion = self.switch_factor(submission, 'colaboracion')
        percepcion = self.switch_factor(submission, 'percepcion')
        autoconciencia_emocional = self.switch_factor(submission, 'autoconciencia')
        autoestima = self.switch_factor(submission, 'autoestima')
        conciencia = self.switch_factor(submission, 'conciencia')
        tolerancia = self.switch_factor(submission, 'tolerancia')
        motivacion = self.switch_factor(submission, 'motivacion')
        comprension = self.switch_factor(submission, 'comprension')
        asertividad = self.switch_factor(submission, 'asertividad')
        desarrollo = self.switch_factor(submission, 'desarrollo')
        liderazgo = self.switch_factor(submission, 'liderazgo')
        manejo_conflictos = self.switch_factor(submission, 'manejo_conflicto')
        violencia = self.switch_factor(submission, 'violencia')
        relacion_social = self.switch_factor(submission, 'relacion')
        optimismo = self.switch_factor(submission, 'optimismo')
        return Analysis(
            empatia=empatia ,colaboracion_cooperacion=colaboracion, percepcion_comprension_emocional=percepcion, 
            autoconciencia_emocional=autoconciencia_emocional, autoestima=autoestima, 
            conciencia_critica = conciencia, tolerancia_frustracion=tolerancia,
            motivacion_logro = motivacion, comprension_organizativa=comprension,asertividad=asertividad,
            desarrollo_relaciones=desarrollo, liderazgo=liderazgo, manejo_conflictos=manejo_conflictos,
            relacion_social=relacion_social, optimismo=optimismo, violencia=violencia)



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

    # Asertividad

    def get_asertividad_by_grouped_sub(self, sub: Submission):
        keywords = ["No", "Yes", "Thanks", "I think that", "I don't agree", "IMO"]
        title_score = self.get_asertividad_by_text(sub.selftext, keywords, 30, 3, 40)
        if(sub.selftext):
            body_score = self.get_asertividad_by_text(sub.title, keywords, 30, 3, 40)
            return self.split_score(title_score, body_score)
        return title_score

    def get_asertividad_by_sub(self, sub: Submission):
        keywords = ["No", "Yes", "Thanks", "I think that", "I don't agree", "IMO"]
        title_score = self.get_asertividad_by_text(sub.selftext, keywords, 55, 2, 25)
        if(sub.selftext):
            body_score = self.get_asertividad_by_text(sub.title, keywords, 55, 2, 25)
            return self.split_score(title_score, body_score)
        return title_score

    def get_asertividad_by_text(self, text: str, keywords: List[str], pol_limit_score:int, word_limit: int, start_limit: int)->float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(text.lower(), 'asertividad')
        match_score = matches*10 if matches <= word_limit else word_limit*10
        start_score = start_limit if self.at_start(text.lower(), keywords) else 0
        score = start_score + pol*pol_limit_score + match_score
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

    # Percepción y comprension emocional

    def get_percepcion_by_grouped_sub(self, sub:Submission):
        title_score = self.get_percepcion_by_text(sub.selftext, 10, 20, 30)
        if(sub.selftext):
            body_score = self.get_percepcion_by_text(sub.title, 10, 20, 30)
            return self.split_score(title_score, body_score)
        return title_score

    def get_percepcion_by_sub(self, sub: Submission) -> float:
        title_score = self.get_percepcion_by_text(sub.selftext, 5, 30, 20)
        if(sub.selftext):
            body_score = self.get_percepcion_by_text(sub.title, 5, 30, 20)
            return self.split_score(title_score, body_score)
        return title_score

    def get_percepcion_by_text(self, text: str, word_limit: int, pol_limit_score:int, subj_limit_score: int) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'percepcion_comprension_emocional')
        match_score = matches*(50/word_limit) if matches <= word_limit else 50
        score = pol*pol_limit_score + subjectivity*subj_limit_score+match_score
        return score

    # Tolerancia a la frustración

    def get_tolerancia_by_grouped_sub(self, sub: Submission) -> float:
        title_score = self.get_tolerancia_by_text(sub.title, 8, 20)
        if(sub.selftext):
            body_score = self.get_tolerancia_by_text(sub.selftext, 8, 20)
            return self.split_score(title_score, body_score)
        return title_score

    def get_tolerancia_by_sub(self, sub:Submission) -> float:
        title_score = self.get_tolerancia_by_text(sub.title, 6, 30)
        if(sub.selftext):
            body_score = self.get_tolerancia_by_text(sub.selftext, 6, 30)
            return self.split_score(title_score, body_score)
        return title_score
    
    def get_tolerancia_by_text(self, text: str, word_limit: int, subj_limit_score: int) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'tolerancia_a_la_frustracion')
        match_score = matches*5 if matches <= word_limit else word_limit*5
        score = pol*40+subjectivity*subj_limit_score+match_score
        return score

    # Motivación al logro

    def get_motivacion_by_sub(self, sub: Submission) -> float:
        title_score = self.get_motivacion_by_text(sub.title)
        if(sub.selftext):
            body_score = self.get_motivacion_by_text(sub.selftext)
            return self.split_score(title_score, body_score)
        return title_score

    def get_motivacion_by_text(self, text: str) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'motivacion_de_logro')
        match_score = matches*5 if matches <= 2 else 10
        score = pol * 60 + subjectivity * 30 + match_score
        return score

    # Conciencia crítica

    def get_conciencia_by_grouped_sub(self, sub: Submission) -> float:
        title_score = self.get_conciencia_by_text(sub.title, 10, 6)
        if(sub.selftext):
            body_score = self.get_conciencia_by_text(sub.selftext, 10, 6)
            return self.split_score(title_score, body_score)
        return title_score

    def get_conciencia_by_sub(self, sub: Submission) -> float:
        title_score = self.get_conciencia_by_text(sub.title, 20, 4)
        if(sub.selftext):
            body_score = self.get_conciencia_by_text(sub.selftext, 20, 4)
            return self.split_score(title_score, body_score)
        return title_score

    def get_conciencia_by_text(self, text: str, pol_limit_score: int, word_limit: int) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'conciencia_critica')
        match_score = matches*5 if matches <= word_limit else word_limit*5
        score = pol * pol_limit_score + subjectivity * 60 + match_score
        return score

    # Comprensión Organizativa

    def get_comprension_by_grouped_sub(self, sub: Submission) -> float:
        title_score = self.get_comprension_by_text(sub.title, 2, 60)
        if(sub.selftext):
            body_score = self.get_comprension_by_text(sub.selftext, 2, 60)
            return self.split_score(title_score, body_score)
        return title_score

    def get_comprension_by_sub(self, sub: Submission) -> float:
        title_score = self.get_comprension_by_text(sub.title, 4, 50)
        if(sub.selftext):
            body_score = self.get_comprension_by_text(sub.selftext, 4, 50)
            return self.split_score(title_score, body_score)
        return title_score

    def get_comprension_by_text(self, text: str, word_limit: int, subj_limit_score: int) -> float:
        blob = TextBlob(text)
        pol = blob.polarity if blob.polarity >= 0 else 0
        subjectivity = blob.subjectivity
        matches = self.match_factor_dict(text.lower(), 'comprension_organizativa')
        match_score = matches*5 if matches <= word_limit else 5*word_limit
        score = pol * 30 + subjectivity*subj_limit_score+match_score
        return score

    # Desarrollo de las relaciones

    def get_desarrollo_by_grouped_sub(self, sub: Submission) -> float:
        votes_score = 60 if sub.upvote_ratio>=0.6 else 0
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(sub.title, 'desarrollo_de_las_relaciones')
        match_score = matches*2 if matches <= 5 else 10
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity >= 0 else 0
            matches = self.match_factor_dict(sub.selftext, 'desarrollo_de_las_relaciones')
            match_score2 = matches*2 if matches <= 5 else 10
            return votes_score + pol*15 + pol2*15 + match_score*0.5 + match_score2*0.5
        else:
            return votes_score + pol*30 + match_score


    def get_desarrollo_by_sub(self, sub: Submission) -> float:
        votes_score = 60 if sub.upvote_ratio>=0.6 else 0
        matches = self.match_factor_dict(sub.title, 'desarrollo_de_las_relaciones')
        match_score = matches*8 if matches <= 5 else 40
        if(sub.selftext):
            matches = self.match_factor_dict(sub.selftext, 'desarrollo_de_las_relaciones')
            match_score2 = matches*8 if matches <= 5 else 40
            return votes_score + match_score*0.5 + match_score*0.5
        else:
            return votes_score + match_score

    # Influencia

    def get_influencia_by_grouped_sub(self, sub: Submission) -> float:
        subscribers = sub.subreddit.subscribers
        subs_score = 60 if subscribers >= 5000 else 0
        votes_score = 20 if sub.upvote_ratio >= 0.2 else 0
        matches = self.match_factor_dict(sub.title, 'influencia')
        match_score = matches*5 if matches <= 4 else 20
        if(sub.selftext):
            matches = self.match_factor_dict(sub.selftext, 'influencia')
            match_score2 = matches*5 if matches <= 4 else 20
            return subs_score + votes_score + match_score*0.5 + match_score2*0.5
        return subs_score + votes_score + match_score
    
    def get_influencia_by_sub(self, sub: Submission) -> float:
        votes_score = sub.upvote_ratio * 70
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(sub.title, 'influencia')
        match_score = matches*5 if matches <= 2 else 10
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity >= 0 else 0
            matches = self.match_factor_dict(sub.selftext, 'influencia')
            match_score2 = matches*5 if matches <= 2 else 10
            return votes_score + pol*10 + pol2 * 10 + match_score * 0.5 + match_score2 * 0.5
        return votes_score + pol*20 + match_score
    


    # Liderazgo

    def get_liderazgo_by_grouped_sub(self, sub: Submission) -> float:
        subscribers = sub.subreddit.subscribers
        subs_score = 20 if subscribers >= 10000 else 0
        matches = self.match_factor_dict(sub.title, 'liderazgo')
        match_score = matches*5 if matches <= 4 else 20
        if(sub.selftext):
            matches = self.match_factor_dict(sub.selftext, 'liderazgo')
            match_score2 = matches*5 if matches <= 4 else 20
            return subs_score + sub.upvote_ratio * 60 + match_score * 0.5 + match_score2 * 0.5
        return subs_score + sub.upvote_ratio * 60 + match_score
    
    def get_liderazgo_by_sub(self, sub: Submission) -> float:
        is_gold = 20 if sub.author.is_gold else 0
        votes_score = sub.upvote_ratio * 30
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(sub.title, 'liderazgo')
        match_score = matches*5 if matches <= 4 else 20
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity >= 0 else 0
            matches = self.match_factor_dict(sub.selftext, 'liderazgo')
            match_score2 = matches*5 if matches <= 4 else 20
            return is_gold + votes_score + pol*15 + pol2 * 15 + match_score * 0.5 + match_score2 * 0.5
        return is_gold + votes_score + pol*30 + match_score

    # Manejo de conflictos

    def get_manejo_conflicto_by_grouped_sub(self, sub: Submission) -> float:
        subreddit : Subreddit = sub.subreddit
        followers: int = subreddit.subscribers
        follow_score = followers*12 if followers <= 5 else 60
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(sub.title, 'manejo_de_conflictos')
        match_score = matches*5 if matches <= 6 else 30
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity >= 0 else 0
            matches2 = self.match_factor_dict(sub.selftext, 'manejo_de_conflictos') 
            match_score2 = matches2*5 if matches2 <= 6 else 30
            return follow_score + mean([pol, pol2])*10 + mean([match_score, match_score2])
        else:
            return follow_score + pol*10 + match_score

    def get_manejo_conflicto_by_sub(self, sub: Submission) -> float:
        votes_score = sub.upvote_ratio * 60
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(sub.title, 'manejo_de_conflictos')
        match_score = matches*5 if matches <= 6 else 30
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity >= 0 else 0
            matches2 = self.match_factor_dict(sub.selftext, 'manejo_de_conflictos')
            match_score2 = matches2*5 if matches2 <= 6 else 30
            return votes_score + mean([pol, pol2])*10 + mean([match_score, match_score2])
        else:
            return votes_score + pol*10 + match_score

    # Relación Social

    def get_relacion_by_grouped_sub(self, sub: Submission) -> float:
        subreddit: Subreddit = sub.subreddit
        follow_score = subreddit.subscribers*4 if subreddit.subscribers <= 10 else 40
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(sub.title, 'relacion_social')
        match_score = matches*5 if matches <= 4 else 20
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity >= 0 else 0
            matches2 = self.match_factor_dict(sub.selftext, 'relacion_social')
            match_score2 = matches2*5 if matches2 <= 4 else 20
            return follow_score + mean([pol, pol2])*40 + mean([match_score, match_score2])
        else:
            return follow_score + pol*40 + match_score

    def get_relacion_by_sub(self, sub: Submission) -> float:
        upvote_score = sub.upvote_ratio * 20
        comment_score = sub.num_comments if sub.num_comments <= 20 else 20
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity >= 0 else 0
        matches = self.match_factor_dict(sub.title, 'relacion_social')
        match_score = matches*5 if matches <= 4 else 20
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity >= 0 else 0
            matches2 = self.match_factor_dict(sub.selftext, 'relacion_social')
            match_score2 = matches2*5 if matches <= 4 else 20
            return upvote_score + comment_score + mean([pol, pol2])*40 + mean([match_score, match_score2])
        else:
            return upvote_score + comment_score + pol*40 + match_score

    # Violencia

    def get_violencia_by_grouped_sub(self, sub: Submission) -> float:
        subreddit: Subreddit = sub.subreddit
        followers = subreddit.subscribers
        follow_score = 2*followers if followers <= 10 else 20
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity <= 0 else 0
        matches = self.match_factor_dict(sub.title, 'violencia')
        match_score = matches*5 if matches <= 6 else 30
        if sub.selftext:
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity <= 0 else 0
            matches2 = self.match_factor_dict(sub.selftext, 'violencia')
            match_score2 = matches2*5 if matches2 <= 6 else 30
            return follow_score + mean([pol, pol2])*-50 + mean([match_score, match_score2])
        else:
            return follow_score + pol*-50 + match_score

    def get_violencia_by_sub(self, sub: Submission) -> float:
        upvote_score = sub.upvote_ratio * 10
        comment_score = sub.num_comments if sub.num_comments <= 10 else 10
        blob = TextBlob(sub.title)
        pol = blob.polarity if blob.polarity <= 0 else 0
        matches = self.match_factor_dict(sub.title, 'violencia')
        match_score = matches*5 if matches <= 6 else 30
        if sub.selftext:
            blob = TextBlob(sub.selftext)
            pol2 = blob.polarity if blob.polarity <= 0 else 0
            matches2 = self.match_factor_dict(sub.selftext, 'violencia')
            match_score2 = matches2*5 if matches2 <= 6 else 30
            return upvote_score + comment_score + mean([pol, pol2])*-50 + mean([match_score, match_score2])
        else:
            return upvote_score + pol*-50 + match_score

    # Optimismo

    def get_optimismo_by_grouped_sub(self, sub: Submission):
        subreddit : Subreddit = sub.subreddit
        follow_score = subreddit.subscribers if subreddit.subscribers <= 10 else 10
        blob = TextBlob(sub.title)
        subj = blob.subjectivity
        matches = self.match_factor_dict(sub.title, 'optimismo')
        match_score = matches * 5 if matches <= 2 else 10
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            subj2 = blob.subjectivity
            matches2 = self.match_factor_dict(sub.selftext, 'optimismo')
            match_score2 = matches2 * 5 if matches2 <= 2 else 10
            return follow_score + mean([subj, subj2])*80 + mean([match_score, match_score2])
        else:
            return follow_score + subj*80 + match_score

    def get_optimismo_by_sub(self, sub: Submission):
        votes_score = sub.upvote_ratio * 10
        comment_score = sub.num_comments if sub.num_comments <= 5 else 5
        blob = TextBlob(sub.title)
        subj = blob.subjectivity
        matches = self.match_factor_dict(sub.title, 'optimismo')
        match_score = 5 if matches > 0 else 0
        if(sub.selftext):
            blob = TextBlob(sub.selftext)
            subj2 = blob.subjectivity
            matches2 = self.match_factor_dict(sub.selftext, 'optimismo')
            match_score2 = 5 if matches > 0 else 0
            return votes_score + comment_score + mean([subj, subj2])*80 + mean([match_score, match_score2])
        else:
            return votes_score + comment_score + subj*80 + match_score


    def split_score(self, title_score: float, body_score: float) -> float:
        return title_score*0.7+body_score*0.3

    def switch_factor(self, sublist: Union[Submission, List[Submission]], factor: str) -> float:
        factor_method = f"get_{factor}_by_sub"    
        method = getattr(self, factor_method)
        if type(sublist) != list:
            return method(sublist)
        resultset = [method(sub) for sub in sublist]
        score = mean(resultset)
        return score
    
    def switch_factor_grouped(self, sublist: Union[Submission, List[Submission]], factor: str) -> float:
        factor_method = f"get_{factor}_by_grouped_sub"    
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
    

