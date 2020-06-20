from typing import List
from random import randint

class Analysis:

    asertividad : float
    autoconciencia_emocional : float
    autocontrol_emocional: float
    autoestima: float
    colaboracion_cooperacion: float
    comprensión_organizativa: float
    comunicacion_asertiva: float
    conciencia_crítica: float
    desarrollar_estimular_otros: float
    desarrollo_relaciones: float
    empatia: float
    influencia: float
    liderazgo : float
    manejo_conflictos: float
    motivacion_logro: float
    optimismo: float
    percepcion_comprension_emocional: float
    relacion_social: float
    tolerancia_frustracion: float
    violencia: float

    __factors = [
        "asertividad", "autoconciencia_emocional", 
        "autocontrol_emocional", "autoestima", 
        "colaboracion_cooperacion", "comprensión_organizativa",
        "comunicacion_asertiva", "conciencia_crítica",
        "desarrollar_estimular_otros", "desarrollo_relaciones",
        "empatia", "influencia", "liderazgo", "manejo_conflictos",
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

    def match_factor_dict(self, text: str, factor : str):
        matches = 0
        for keyword in self.dictionary["factores"][factor]:
            if keyword.lower() in text:
                matches += 1
        return matches
    
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