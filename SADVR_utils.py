import requests
import json
import pandas as pd
from ast import literal_eval
from collections import Counter

#################################################################
##### Fonctions pour importer/updater les données

baseURI = 'https://www.recherche.umontreal.ca/vitrine/rest/api/1.7/umontreal'
mapping = {
    'facultes': f'{baseURI}/ressource/faculte',
    'departements': f'{baseURI}/ressource/departement',
    'unitesAdministratives': f'{baseURI}/ressource/uniteadmin',
    'fonctions': f'{baseURI}/ressource/fonction',
    'individus' : f'{baseURI}/id/individu',
    "programmesEtude": f'{baseURI}/ressource/programme',
    "domainesEtude": f'{baseURI}/ressource/domaineetude',
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

def getAllTables(mapping: dict = mapping):
    """
    Cette fonction permet d'extraire une table de données pour une liste de ressources de l'API SADVR et exporte toutes les 
    tables correspondantes dans des fichiers distincts au format CSV. (Un CSV par ressource)
    """
    for ressource in mapping:
        output = getTable(ressource)
        if type(output) == pd.DataFrame:
            output.to_csv(f'tables/SADVR_{ressource}.csv', index=False)

def getInfoIndividus(id_individus: list, CSVexport=False) -> pd.DataFrame :
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
            output.append(json.loads(requests.get(uri).text)['data'][0])

        except Exception as e:
            print(id, e)

    output = pd.DataFrame(output).drop_duplicates()

    if(CSVexport):
        output.to_csv('tables/SADVR_infoIndividus.csv', index=False)
    return output

def updateInfoIndividus(tableInfoIndividus: pd.DataFrame = pd.read_csv('tables/SADVR_infoIndividus.csv')) -> pd.DataFrame:
    """
    Cette fonction prend en paramètre un dataframe contenant les informations sur les individus du SADVR
    et retourne une version actualisée de celui-ci en y ajoutant l'information associée aux individus
    dernièrement ajoutés.\nNormalement, le dataframe d'entrée a été obtenu par l'exécution de la 
    fonction getInfoIndividus sur l'ensemble des individus. La requête étant relativement longue à exécuter sur 
    tous les individus à la fois, la présente fonction est conçue pour éviter d'avoir à extraire toutes les
    données à chaque fois et plutôt n'extraire que les nouvelles informations.
    """
    all_ids = [x['idsadvr'] for x in getTable('individus').to_dict('records')]
    current_ids = tableInfoIndividus['idsadvr'].tolist()

    # Extraire la liste des ids qui ne se trouvent pas dans la table SADVR_infoIndividus
    ids = [x for x in all_ids if not x in current_ids]

    # Ajouter les nouveaux ids à la table
    if (len(ids) > 0):
        new_info = getInfoIndividus(ids)
        output = pd.concat([tableInfoIndividus, new_info]).drop_duplicates()
        output.to_csv('tables/SADVR_infoIndividus.csv', index=False)

        return output
    
    else:
        return tableInfoIndividus

def getAllProfs() -> pd.DataFrame:
    """
    Cette fonction envoie une requête SOLR dans le répertoire des professeurs de l'API SADVR, récupère les informations 
    relatives à tous les professeurs dans un DataFrame et les exporte dans un fichier tabulaire (CSV).
    """
    index = 0
    res = json.loads(requests.get(f'{baseURI}/recherche/professeur/select?q=ID:*&start={index}').text)
    nbResults = res['paginationSOLR']['numFound']

    dataProfs = []
    for i in range(0, nbResults, 20):
        res = json.loads(requests.get(
            f'{baseURI}/recherche/professeur/select?q=ID:*&start={index}&rows=20'
            ).text)['data']
        
        dataProfs += res
        index += 20

    output = pd.DataFrame(dataProfs)
    output.to_csv('tables/SADVR_professeurs.csv', index=False)

    return output

#################################################################
###### Fonctions pour nettoyer, normaliser ou filtrer les données

# Séparer les colonnes qui contiennent des données structurées en JSON en muliples colonnes distinctes
def explodeNormalize(df: pd.DataFrame, columns: list):
    """
    Cette fonction prend en paramètre un DataFrame et une liste contenant les noms des colonnes à normaliser.
    Elle retourne le DataFrame modifié, où les colonnes spécifiées ont été normalisées. 
    """
    for col in columns:
        try:
            df.loc[:, col] = df[col].transform(lambda x: literal_eval(str(x)))
        except:
            df.loc[:, col] = df[col].fillna('[]').transform(lambda x: literal_eval(str(x)))
        
        dTypeCol = Counter(df[col].apply(lambda x: type(literal_eval(str(x)))).tolist()).most_common(1)[0][0]
        if dTypeCol == list:
            df = df.explode(col).reset_index(drop=True)
        
        dfTemp = pd.json_normalize(df[col]).add_prefix(f'{col}.') 
        
        df = pd.concat([df, dfTemp], axis=1).drop(col, axis=1)

    return df
