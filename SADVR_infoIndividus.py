import requests
import json
import pandas as pd
from SADVR_getTables import getTable

def getInfoIndividus(id_individus: list) -> pd.DataFrame :
    """ 
    Cette fonction prend en paramètre une liste d'identifiants associés à des individus inscrits dans le SADVR
    et retourne un DataFrame contenant les informations pour chacun de ces individus.\nNormalement, la liste d'individu
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


def updateInfoIndividus(tableInfoIndividus: pd.DataFrame) -> pd.DataFrame:
    """
    Cette fonction prend en paramètre un dataframe contenant les informaitons sur les individus du SADVR
    et retourne une version actualisée de celui-ci en y ajoutant l'information associée aux individus
    dernièrement ajoutés au SADVR.\nNormalement, le dataframe d'entrée a été obtenu par l'exécution de la 
    fonction getInfoIndividus sur l'ensemble des individus. La requête étant relativement longue à exécuter sur 
    tous les individus à la fois, la présente fonction est conçue pour éviter d'avoir à extraire toutes les
    données à chaque fois et plutôt n'extraire que les nouvelles informations.
    """
    all_ids = [x['idsadvr'] for x in getTable('individus').to_dict('records')]
    current_ids = tableInfoIndividus['idsadvr'].tolist()

    # Extraire la liste des ids qui ne se trouvent pas dans la table SADVR_infoIndividus
    ids = [x for x in all_ids if not x in current_ids]

    # Ajouter les nouveaux ids à la table
    new_info = getInfoIndividus(ids)
    output = pd.concat([tableInfoIndividus, new_info])
    output.to_csv('tables/SADVR_infoIndividus.csv')

    return output


# current_info = pd.read_csv('tables/SADVR_infoIndividus.csv')
# updateInfoIndividus(current_info)