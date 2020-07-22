from typing import List
from random import randint

class Analysis:

    asertividad : float
    autoconciencia_emocional : float
    autoestima: float
    colaboracion_cooperacion: float
    comprension_organizativa: float
    conciencia_critica: float
    desarrollar_estimular: float
    empatia: float
    liderazgo : float
    manejo_conflictos: float
    motivacion_logro: float
    optimismo: float
    percepcion_comprension_emocional: float
    relacion_social: float
    tolerancia_frustracion: float
    violencia: float

    __factors = [
        "asertividad", "autoconciencia_emocional", "autoestima", 
        "colaboracion_cooperacion", "comprension_organizativa", "conciencia_critica",
        "desarrollar_estimular",
        "empatia", "liderazgo", "manejo_conflictos",
        "motivacion_logro", "optimismo", "percepcion_comprension_emocional",
        "relacion_social", "tolerancia_frustracion", "violencia"
    ]

    def __init__(self, *args, **kwargs):
        vars(self).update(kwargs)

    def toDict(self):
        factors : List[str] = [i for i in self.__dict__.keys() if i[:1] != '_']
        dic = dict()
        for factor in factors:
            dic[factor] = getattr(self, factor)
        return dic
    
    def toRandomDict(self):
        dic = dict()
        for factor in self.__factors:
            dic[factor] = randint(0, 100)
        return dic

class BaseAnalyzer:

    dictionary : dict

    def __init__(self, dictionary: dict):
        self.dictionary = dictionary

    def match_factor_dict(self, text: str, factor : str) -> int:
        matches = 0
        for keyword in self.dictionary["factores"][factor]:
            if keyword.lower() in text:
                matches += 1
        return matches
    
    def at_start(self, text: str, sentences: List[str]) -> bool:
        first_sentence = text.split(",")[0].lower()
        for keyword in sentences:
            if first_sentence == keyword:
                return True
        return False

    def getRandom(self) -> Analysis:
        analysis = Analysis().toRandomDict()
        return analysis

    def analyze_user(self) -> Analysis:
        pass

    def get_asertividad(self):
        pass

    def get_liderazgo(self):
        pass

class BaseAPIWrapper:

    analyzer : BaseAnalyzer

    def __init__(self, analyzer : BaseAnalyzer):
        self.analyzer = analyzer
    
    def analyze_user_by_id(self, id : str):
        pass
