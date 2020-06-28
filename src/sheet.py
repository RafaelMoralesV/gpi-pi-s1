import pandas as pd
from typing import List, Union, Dict

def str_to_sheet(data: str):
    dfdict: dict = pd.read_excel(data).dropna().to_dict()
    sheet: Dict[str, List[str]] = {}
    for key in list(dfdict.keys()):
        sheet[key] = list(dfdict[key].values())
    return sheet