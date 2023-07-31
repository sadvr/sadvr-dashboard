import requests
import json
import pandas as pd
from ast import literal_eval
from collections import Counter


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

def getInfoIndividus(id_individus: list) -> pd.DataFrame :
    """ 
    Cette fonction prend en paramètre une liste d'identifiants associés à des individus inscrits dans le SADVR
    et retourne un DataFrame contenant les informations pour chacun de ces individus.\nNormalement, la liste d'individu
    a été obtenue par une première requête envoyée à l'URI 'id/individu'
    """
    baseURI = 'https://www.recherche.umontreal.ca/vitrine/rest/api/1.7/umontreal'

    output = []
    for id in id_individus:
        try:
            uri = f'{baseURI}/info/individu?idsadvr={id}'
            output.append(json.loads(requests.get(uri).text)['data'][0])

        except Exception as e:
            print(id, e)

    output = pd.DataFrame(output)
    output = output[
        ['idsadvr', 'sexe', 'langues', 'institution', 'unitesRecherche', 'paysCode', 
        'paysNom', 'formations', 'prix', 'publication', 'communication']]
    
    return output

def getAllProfsSOLR() -> pd.DataFrame:
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

def updateInfoProfs(tableInfoProfs: pd.DataFrame = pd.read_csv('tables/SADVR_professeurs.csv')) -> pd.DataFrame:
    """
    Cette fonction prend en paramètre un dataframe contenant les informations sur les professeurs du SADVR
    et retourne une version actualisée de celui-ci en y ajoutant l'information associée aux professeurs
    dernièrement ajoutés.\nNormalement, le dataframe d'entrée a été obtenu par l'exécution de la 
    fonction getInfoProfs sur l'ensemble des individus. La requête étant relativement longue à exécuter sur 
    tous les professeurs à la fois, la présente fonction est conçue pour éviter d'avoir à extraire toutes les
    données à chaque fois et plutôt n'extraire que les nouvelles informations.
    """

    # Vérifier s'il y a des nouvelles informations en comparant le nombre d'enregistrements dans le répertoire des 
    # professeurs au nombre d'enregistrement dans la table actuelle.
    current_ids = tableInfoProfs['idsadvr'].tolist()
    nbActualData = len(current_ids)

    res = json.loads(requests.get(f'{baseURI}/recherche/professeur/select?q=ID:*').text)
    nbResultsSOLR = res['paginationSOLR']['numFound']

    # Si de nouveaux professeurs ont été ajoutés au répertoire depuis le dernier import, nous allons les ajouter à la table
    if(nbResultsSOLR > nbActualData):
        dataProfs = getAllProfsSOLR()
        all_ids = dataProfs['idsadvr'].tolist()

        # Extraire la liste des ids qui ne se trouvent pas dans la table SADVR_infoIndividus
        ids = [x for x in all_ids if not (x in current_ids)]

        # Ajouter les nouveaux ids à la table
        new_info = getInfoIndividus(ids)
        new_info = dataProfs.merge(new_info, on='idsadvr')

        output = pd.concat([tableInfoProfs, new_info])
        output = output[output['nom'] != '?_?']

        columns = pd.read_csv('columns.csv')['columns'].tolist()
        output = output[[x for x in output.columns if x in columns]]
        
        # Réexporter la table contenant les informations pour les nouveaux individus
        output.sort_values(by='idsadvr').to_csv('tables/SADVR_professeurs.csv', index=False)
        return output
        
    else:
        return tableInfoProfs
    

##### Fonctions pour nettoyer, normaliser, mettre en forme ou filtrer les données
# Séparer les colonnes qui contiennent des données structurées en JSON en muliples colonnes distinctes
def explodeNormalize(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Cette fonction prend en paramètre un DataFrame et le nom d'une colonne à normaliser.
    Elle retourne le DataFrame modifié, où la colonne spécifiée a été normalisée. 
    """
    try:
        df.loc[:, column] = df[column].transform(lambda x: literal_eval(str(x)))
    except:
        df.loc[:, column] = df[column].fillna('[]').transform(lambda x: literal_eval(str(x)))
    
    dTypeCol = Counter(df[column].apply(lambda x: type(literal_eval(str(x)))).tolist()).most_common(1)[0][0]
    if dTypeCol == list:
        df = df.explode(column).reset_index(drop=True)
    
    dfTemp = pd.json_normalize(df[column]).add_prefix(f'{column}.') 
    
    df = pd.concat([df, dfTemp], axis=1).drop(column, axis=1)

    return df

def groupOtherValues(df: pd.DataFrame, threshold: int = 6) -> pd.DataFrame:
    """
    Cette fonction prend en paramètre un objet DataFrame contenant une distirbution de fréquences et un nombre entier 
    représentant le nombre de valeurs à représenter dans un graphique. Elle retourne le DataFrame modifié en regroupant toutes 
    les autres valeurs dans une catégorie "Autre", permettant ainsi d'alléger la visualisaiton en réduisant le nombre de 
    catégories qui seornt affichées dans une visualisation.

    Par défaut, la fonction prend les 6 principales valeurs et groupe les autres dans la catégorie "Autre".
    
    À noter que la colonne contenant les fréquences associées aux catégories doit s'appeler 'count'.
    """
    top_values = df.head(threshold)
    other_values_count = df[threshold:]['count'].sum()
    col = df.columns[0]
    other_values = pd.DataFrame({col: ['Autre'], 'count': [other_values_count]})
    
    return pd.concat([top_values, other_values])

def plotVariable(df: pd.DataFrame, variable: str, mapping=None) -> dict:
    """
    Cette fonction prend en paramètre un objet DataFrame et un champ d'intérêt à visualiser dans un graphique.
    Elle calcule les fréquences associées aux différentes catégories de la variable d'intérêt et retourne un objet 
    dictionnaire contenant les champs suivants:  
    - Labels: les noms des catégories de données
    - Values: les fréquences associées aux catégories de données

    Un paramètre optionnel permet de spécifier un mapping à effectuer entre les noms des catégories et d'autres étiquettes.
    Par exemple, pour le genre, on pourrait avoir un mapping spécifiant 'M' -> 'Hommes', 'F' -> 'Femmes'. Un mapping peut
    également être spécifié pour les noms des fonctions de professeurs associés à un codeSad.

    À noter que le DataFrame doit contenir une colonne appelée 'idsadvr'.
    """

    data = df[['idsadvr', variable]].drop_duplicates()
    frequences = pd.DataFrame(data[variable].value_counts()).reset_index()
    
    labels = frequences[variable].tolist()

    if(mapping):
        labels = frequences[variable].map(mapping).tolist()
        frequences['mapping'] = frequences[variable].map(mapping)
                
    frequences.to_csv(f'tables/demographics/{variable}.csv', index=False)                
    
    # values = frequences['count'].tolist()

    # output = {
    #     'labels': labels, 
    #     'count': values
    # }

    # return output

    return frequences
