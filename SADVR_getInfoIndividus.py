import requests
import json
import pandas as pd

def getInfoIndividus(id_individus: list) -> pd.DataFrame :
    """ 
    Cette fonction prend en paramètre une liste d'identifiants associés à des individus inscrits dans le SADVR
    et retourne un DataFrame contenant les informations pour chacun de ces individus. Normalement, la liste d'individu
    a été obtenue par une première requête envoyée l'URI 'id/individu'
    """
    baseURI = 'https://www.recherche.umontreal.ca/vitrine/rest/api/1.7/umontreal'

    output = []
    for id in id_individus:
        try:
            uri = f'{baseURI}/info/individu?idsadvr={id}'
            output.append(json.loads(requests.get(uri).text)['data'])

        except Exception as e:
            print(id, e)

    output.to_csv('tables/infoIndividus.csv', index=False)
    return output