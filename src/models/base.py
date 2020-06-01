
class Analysis:

    asertividad : float
    liderazgo : float

    def __init__(self, *args, **kwargs):
        self.liderazgo = kwargs.pop('liderazgo')
        self.asertividad = kwargs.pop('asertividad')

    def toDict(self):
        return {
            "asertividad" : self.asertividad,
            "liderazgo" : self.liderazgo
        }



class BaseAnalyzer:

    dictionary : dict

    def __init__(self, dictionary: dict):
        self.dictionary = dictionary

    def match_factor_dict(self, text: str, factor : str):
        matches = 0
        for keyword in self.dictionary["factores"][factor]:
            matches += text.find(keyword)
        return matches

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