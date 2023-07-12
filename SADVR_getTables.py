import requests
import json
import pandas as pd

baseURI = 'https://www.recherche.umontreal.ca/vitrine/rest/api/1.7/umontreal'
mapping = {
    'facultes': f'{baseURI}/ressource/faculte',
    'departements': f'{baseURI}/ressource/departement',
    'unitesAdministratives': f'{baseURI}/ressource/uniteadmin',
    'fonctions': f'{baseURI}/ressource/fonction',
    "programmesEtude": f'{baseURI}/ressource/programme',
    "individus" : f'{baseURI}/id/individu',
    "domainesEtude": f'{baseURI}/ressource/domaineetude',
    "expertisesRecherche": f'{baseURI}/ressource/expertiserech',
    "secteursRecherche": f'{baseURI}/ressource/secteurrech',
    "disciplines": f'{baseURI}/ressource/discipline',
    "etablissementsAffilies": f'{baseURI}/ressource/etablaffilie',
    "langues": f'{baseURI}/ressource/langue',
    "typesUnitesRecherche": f'{baseURI}/ressource/typeuniterech'
    }

def getTable(ressourceSADVR:str) -> pd.DataFrame:
        """
        Cette fonction prends en paramètre le nom d'une ressource de l'API SADVR (ex. 'facultes', 'departements', 'individus')
        et retourne un DataFrame contenant une représentation tabulaire des données retournées par l'API pour cette ressource.
        https://wiki.cen.umontreal.ca/pages/viewpage.action?pageId=51642901#APIREST%E2%80%93Descriptiontechnique-Serviced'expositiondesressources
        """       
        try:
            data = pd.DataFrame(json.loads(requests.get(mapping[ressourceSADVR]).text)['data'])
            if 'noms' in data.columns:
                data = data.explode('noms').reset_index(drop=True)
                data = pd.json_normalize(data.to_dict('records'))
                data = data[data['noms.codeLangue'] == 'fre']
            
            return data
                   
        except Exception as e:
             print(ressourceSADVR, e)

def getAllTables(mapping=mapping):
    for ressource in mapping:
        output = getTable(ressource)
        if type(output) == pd.DataFrame:
            output.to_csv(f'tables/SADVR_{ressource}.csv', index=False)