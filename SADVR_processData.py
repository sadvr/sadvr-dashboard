import pandas as pd
from ast import literal_eval
from collections import Counter

# Séparer les colonnes qui contiennent des données structurées en JSON en muliples colonnes distinctes
def explodeNormalize(df: pd.DataFrame, columns: list, ):
    """
    Cette fonction prend en paramètre un DataFrame et une liste contenant les noms des colonnes à normaliser.
    Elle retourne le DataFrame modifié
    """
    for col in columns:
        try:
            df.loc[:, col] = df[col].transform(lambda x: literal_eval(str(x)))
        except:
            df.loc[:, col] = df[col].fillna('[]').transform(lambda x: literal_eval(str(x)))
        
        dTypeCol = Counter(df[col].astype(str).apply(lambda x: type(literal_eval(x))).tolist()).most_common(1)[0][0]
        if dTypeCol == list:
            df = df.explode(col).reset_index(drop=True)
        
        dfTemp = pd.json_normalize(df[col]).add_prefix(f'{col}.') 
        
        df = pd.concat([df, dfTemp], axis=1).drop(col, axis=1)

    return df
