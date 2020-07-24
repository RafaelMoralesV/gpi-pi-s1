import pandas as pd
from typing import List, Union, Dict

def str_to_sheet(data: str):
    dfdict: dict = pd.read_excel(data)
    dfdict = dfdict.to_dict()
    sheet: Dict[str, List[str]] = {}
    for key in list(dfdict.keys()):
        sheet[key] = []
        for value in list(dfdict[key].values()):
            if type(value) == str:
                sheet[key].append(value)
    return sheet
