from utils.sadvr_utils import *
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
from slugify import slugify
import json
import math

# Charger les données
data = updateInfoProfs()

# Expertises de recherche
expertises = data[[
    'idsadvr',
    'affiliations',
    'etablissementsAffilies',
    'expertise'
]]

toNormalize = [
    'affiliations',
    'etablissementsAffilies',
    'expertise',
    'expertise.disciplines'
]

for c in toNormalize:
    expertises = explodeNormalize(expertises, c)

drop = [
    'affiliations.courrielInstitutionnel', 
    'affiliations.immeuble', 
    'affiliations.fonction.codeSad', 
    'affiliations.fonction.nom', 
    'affiliations.local', 
    'affiliations.exclusion', 
    'affiliations.exclusionTel',
    'affiliations.uniteAdministrative.codeSad',
    'affiliations.uniteAdministrative.nom',
    'affiliations.telephone.numero',
    'affiliations.telephone.poste',
    'expertise.phraseCle'
]

expertises = expertises.drop(columns=drop)

### Expertises de recherche - mots-clés
motsCles = data[['idsadvr', 'expertise']]
departements = getTable('individus')[['idsadvr', 'uniteAdmin']]
motsCles = motsCles.merge(departements, on='idsadvr')

motsCles['département'] = motsCles['uniteAdmin'].astype(str).apply(uniteAdminDepartement)
motsCles = motsCles.drop(columns='uniteAdmin')

## Normalisation des données
toNormalize = ['expertise', 'expertise.disciplines']
for c in toNormalize:
    motsCles = explodeNormalize(motsCles, c)

motsCles = motsCles.dropna(subset = 'expertise.disciplines.uid') 
motsCles = motsCles[motsCles['expertise.motsCles'].astype(str) != '[]']
motsCles = motsCles[motsCles['département'].astype(str) != 'None']

motsCles = explodeNormalize(motsCles, 'expertise.motsCles')

motsCles = motsCles[motsCles['expertise.motsCles.ordre'].astype(int) <=3]
motsCles.loc[:, 'expertise.motsCles.nom'] = motsCles['expertise.motsCles.nom'].apply(lambda x: x.replace("COVID19", "COVID-19"))

motsCles = motsCles[[
    'idsadvr',
    'département',
    'expertise.disciplines.uid',
    'expertise.disciplines.codeLangue',
    'expertise.disciplines.nom', 
    'expertise.motsCles.uid', 
    'expertise.motsCles.nom', 
    'expertise.motsCles.codeLangue'
]]

motsCles = motsCles.sort_values(by=[
    'expertise.disciplines.uid',
    'expertise.disciplines.codeLangue',
    'expertise.motsCles.uid',
    'expertise.motsCles.codeLangue'], 
    ascending=[True, False, True, False])

motsCles = motsCles.drop_duplicates(subset=[
    'idsadvr',
    'expertise.motsCles.uid',
    'expertise.disciplines.uid'
])

motsCles = motsCles.drop(columns=[
    'expertise.disciplines.codeLangue', 
    'expertise.motsCles.codeLangue']
)

# Données sociodémographiques
demographics = data[[
    'idsadvr',
    'sexe',
    'langues',
    'formations',
    'affiliations'
]]

fonctionsProf = pd.read_csv('utils/fonctionsProfs.csv')['codeSad'].tolist()
toNormalize = [
    'langues',
    'affiliations',
    'formations',
    'formations.disciplines',
    'formations.institutions'
]

for c in toNormalize:
    demographics = explodeNormalize(demographics, c)

columns = pd.read_csv('utils/columnsDemographics.csv')['columns'].tolist()
demographics = demographics[[x for x in demographics.columns if x in columns]]

demographics = demographics[demographics['affiliations.fonction.codeSad'].isin(fonctionsProf)]

### Analyses sociodémographiques
### 1e visuel : 4 mesures "Count"
# 1: nombre de professeurs
nbProfs = len(data.drop_duplicates(subset='idsadvr'))

# 2: nombre de facultés et écoles
nbFacultes = len(getTable('facultes'))

# 3: nombre de départements
nbDepartements = len(getTable('departements'))


# 4: Nombre d'établissements affiliés
etablissementsAffilies = data[[
    'idsadvr',
    'etablissementsAffilies'
]]

etablissementsAffilies = explodeNormalize(etablissementsAffilies, 'etablissementsAffilies')
etablissementsAffilies = etablissementsAffilies.dropna(subset='etablissementsAffilies.nom')
etablissementsAffilies = etablissementsAffilies.drop_duplicates(subset=(['idsadvr', 'etablissementsAffilies.nom']))
etablissementsAffilies = pd.DataFrame(plotVariable(etablissementsAffilies, 'etablissementsAffilies.nom'))
nbEtablissementsAffilies = len(etablissementsAffilies)

# Genre
mappingGenre = {
    'M': 'Homme', 
    'F': 'Femme', 
    'A': 'Autre'
}
genre = data[['idsadvr', 'sexe']]

genre['genre'] = genre['sexe'].map(mappingGenre)

freqGenre = pd.DataFrame(plotVariable(genre, 'genre'))

# Créer la table de fréquence
genreDepartement = expertises.merge(genre, on='idsadvr')[
    ['idsadvr', 'genre', 'affiliations.departement.nom']
]
genreDepartement = genreDepartement.dropna(
    subset=['genre', 'affiliations.departement.nom']
).drop_duplicates()

# Group by 'faculty' and 'discipline' and count the number of professors in each group
freqGenreDepartement = genreDepartement.groupby(['affiliations.departement.nom', 'genre'])['idsadvr'].count().reset_index()

freqGenreDepartement = freqGenreDepartement.rename(
    columns={'idsadvr': 'count', 'affiliations.departement.nom' : 'Département'})

# Ajouter une option pour voir tous les départements confondus (default)
freqGenre = freqGenre.to_dict('records')
freqGenre

freqGenreDepartement = freqGenreDepartement.to_dict('records')
for g in freqGenre:
    freqGenreDepartement.append({'Département': 'Tous les départements', 'genre': g['labels'], 'count': g['count']})

freqGenreDepartement = pd.DataFrame(freqGenreDepartement)
freqGenreDepartement['noms'] = freqGenreDepartement['Département'].apply(renameLongLabels)

freqGenreDepartement = freqGenreDepartement.sort_values(
    by=['count','genre'], 
    ascending=[False, True]
)


freqGenreDepartement = freqGenreDepartement[~freqGenreDepartement['Département'].str.contains('Direction de')]

defaultCat = 'Tous les départements'
mask = freqGenreDepartement['Département'] == defaultCat

freqGenreDepartement = pd.DataFrame(pd.concat([
    freqGenreDepartement[mask].sort_values(by='Département'), 
    freqGenreDepartement[~mask].sort_values(by='Département')
]))

def generate_pie_chart(selected_department):
    filtered_df = freqGenreDepartement[freqGenreDepartement['Département'] == selected_department]
    filtered_df = filtered_df.sort_values(by='count', ascending=False)
    
    # Define colors for each category
    category_colors = {'Homme': '#636efa', 'Femme': '#ef553b', 'Autre': 'lightgray'}
    
    fig = go.Figure(px.pie(
        filtered_df,
        names= 'genre', 
        color = 'genre',
        values=filtered_df['count'],
        hole=0.6,
        color_discrete_map = category_colors,
        category_orders = {'genre': ["Homme", "Femme", "Autre"]} 
        )
    )

    fig.update_layout(
        margin=dict(l=0, r=70, t=10, b=10),
        legend=dict(
            x=0,  # Position the legend to the left
            y=0.5  
        )
    )

    return fig

# Create a figure for each category
genreDepartement = {}

for departement in freqGenreDepartement['Département'].unique():
    fileName = f'figures/genreDepartement/{slugify(departement)}.html'
    with open(fileName, 'w', encoding='utf-8') as f:
        f.write(generate_pie_chart(departement).to_html(full_html=False, include_plotlyjs='cdn'))

    genreDepartement[departement] = "../"+fileName

freqGenreDepartement = freqGenreDepartement[['Département',	'genre', 'count']]
freqGenreDepartement = freqGenreDepartement.rename(columns={'count':'N',  'genre':'Genre'})

# Pays d'obtention du dernier diplôme
paysFormation = pd.DataFrame(plotVariable(demographics, 'formations.institutions.paysNom'))

# Année d'obtention du dernier diplôme - selon le genre
# D'abord filtrer pour ne conserver que le dernier diplôme obtenu
anneeDiplome = demographics.sort_values(['idsadvr', 'formations.annee'], ascending=[True, False])
anneeDiplome['genre'] = anneeDiplome['sexe'].map(mappingGenre)

anneeDiplome = anneeDiplome[
    ['idsadvr',
    'genre',
    'formations.annee']
].dropna(subset='formations.annee')

anneeDiplome = anneeDiplome.drop_duplicates(subset=['idsadvr', 'formations.annee'])

anneeDiplomeGenre =  pd.DataFrame(anneeDiplome.drop(columns='idsadvr').value_counts()).reset_index().sort_values(by='formations.annee', ascending=True)

figAnneDiplomeGenre = px.line(
    anneeDiplomeGenre, 
    x = 'formations.annee', 
    y = 'count',
    color = 'genre',
    title = "Année d'obtention du dernier diplôme selon le genre",
    line_shape = 'spline')

#figAnneDiplomeGenre.update_traces(mode="markers+lines", hovertemplate=None)
figAnneDiplomeGenre.update_layout(
    title_x=0.005,
    hovermode="x unified",
    xaxis_title=None,  # Hide x-axis title
    yaxis_title=None,   # Hide y-axis title
    legend=dict(font=dict(size= 12))
)

figAnneDiplomeGenre.update_layout(margin=dict(l=30))

# Rang professoral par genre
fonctionGenre = demographics[[
    'idsadvr', 
    'sexe',
    'affiliations.fonction.codeSad']
    ].drop_duplicates()

freqFonctionGenre = pd.DataFrame(fonctionGenre[
    ['sexe', 'affiliations.fonction.codeSad']
    ].value_counts()).reset_index()

mapping = pd.read_csv('tables/SADVR_fonctions.csv')[['codeSad', 'nomM']].to_dict('records')
mapping = {x['codeSad'] : x['nomM'] for x in mapping}

freqFonctionGenre['fonction'] = freqFonctionGenre['affiliations.fonction.codeSad'].map(mapping)

freqFonctionGenre['genre'] = freqFonctionGenre['sexe'].map(mappingGenre)

freqFonctionGenre = freqFonctionGenre[
    ['genre', 
    'fonction',  
    'count']
]

freqFonctionGenre = freqFonctionGenre[freqFonctionGenre['genre'] != 'Autres']
freqFonctionGenre = freqFonctionGenre[
    freqFonctionGenre['fonction'] != 'Professeur de formation pratique titulaire'] # anomalie

freqFonctionGenre = freqFonctionGenre.sort_values(by='count', ascending=False)

freqFonctionGenre['noms'] = freqFonctionGenre['fonction'].apply(lambda x: renameLongLabels(x))
figFonctionGenre = px.bar(
    freqFonctionGenre.sort_values(by="count", ascending=True),
    y = 'noms',
    x = 'count',
    hover_name='fonction',
    color = 'genre',
    barmode='group',
    orientation = 'h',
    height = 1800
)

figFonctionGenre.update_layout(
    yaxis_title=None,
    xaxis_title=None,
    margin=dict(l=60, r=40, t=30, b=0), 
    legend=dict(yanchor="top",y=1,xanchor="right", x=1.15)
)

# Adjust the bar width and spacing
figFonctionGenre.update_traces(
    width = 0.2  # Set the bar width (0.8 is the default, adjust as needed)
)

# Langues parlées
langueParle = demographics[demographics['langues.medium'] == 'Oral'].drop(
    columns=['langues.medium']
)

langueParle = pd.DataFrame(plotVariable(langueParle, 'langues.nom'))
langueParle = groupOtherValues(langueParle)

figLanguesParlees = px.pie(
    langueParle,
    values = langueParle['count'], 
    names = langueParle['labels'], 
    title='Langues parlées',
    hole=0.6,
    category_orders={'langues.nom': 
        ['Français', 
        'Anglais',
        'Espagnol; castillan', 
        'Allemand', 
        'Italien',
        'Arabe',
        'Autre']
    }
)


# Langues écrites
langueEcrite = demographics[demographics['langues.medium'] == 'Écrit'].drop(columns=['langues.medium'])
langueEcrite = pd.DataFrame(plotVariable(langueEcrite, 'langues.nom'))
langueEcrite = groupOtherValues(langueEcrite)

order = [x for x in langueEcrite['labels'] if not (x == 'Autre')] + ['Autre']

figLanguesEcrites = px.pie(
    langueEcrite,
    values = langueEcrite['count'], 
    names = langueEcrite['labels'], 
    title='Langues écrites',
    hole=0.6,
    category_orders={'labels': order},
)

# Pays de formation - représentation géographique
# Passer du code iso-2 à iso-3 pour que ce soit conforme à ce qu'attent Plotly
mappingIso = pd.read_csv('utils/mappingPays_iso.csv', sep=';').to_dict('records')
mappingIso = {x['Alpha-2 code'] : x['Alpha-3 code'] for x in mappingIso}

# Dresser le mapping entre les codes iso-2 aux noms de pays
mappingNomsPays = (demographics[
    ['formations.institutions.paysNom', 
    'formations.institutions.paysCode']
    ].drop_duplicates()).to_dict('records')
mappingNomsPays = {
    x['formations.institutions.paysCode'] : x['formations.institutions.paysNom'] for x in mappingNomsPays
}

mappingPays = pd.read_csv('utils/mappingPays_iso.csv', sep=';', encoding='utf-8')
mappingPays['nomPaysFr'] = mappingPays['Alpha-2 code'].map(mappingNomsPays)
mappingPays = mappingPays.dropna(subset='nomPaysFr').to_dict('records')

mappingNomsPays = {x['Alpha-2 code'] : x['nomPaysFr'] for x in mappingPays}

# Construire la table de données
paysFormation = pd.DataFrame(plotVariable(demographics, 'formations.institutions.paysCode'))
paysFormation['nomPaysFR'] = paysFormation['labels'].map(mappingNomsPays)
paysFormation['codePays'] = paysFormation['labels'].map(mappingIso)

figPaysFormation = px.scatter_geo(
    paysFormation, 
    locations="codePays",
    locationmode = 'ISO-3',
    hover_name = 'nomPaysFR',
    size="count",
    size_max = 50,
    height=440,
    projection = 'equirectangular',
    
)

# Customize the layout
figPaysFormation.update_geos(
    showcoastlines=False,  # Hide coastlines/borders
    showland=True,  # Hide land area color
    landcolor = '#E8E8E8',
    showframe=False,  # Hide frame/borders
    projection_scale = 1.2,  # Adjust the projection scale to fit the map better
    center=dict(lon=20, lat=18),  # Set the center of the map to exclude Antarctica
)

figPaysFormation = figPaysFormation.update_layout( 
    margin=dict(t=0, l=0, r=0, b=0),
    title_x=0.2, 
)

paysFormation = paysFormation[['nomPaysFR', 'count']].rename(columns={'nomPaysFR': 'Pays', 'count': 'N'})

### Analyses expertises de recherche
# Éléments de visuel
shadow = '2px 2px 6px lightgrey'

#### Construire les tables et les figures à inclure dans le board
# Nombre de professeurs par faculté
facultes = pd.DataFrame(plotVariable(expertises, 'affiliations.faculte.nom'))[:-2].sort_values(by='count', ascending=False)

# Secteurs
facultes['noms'] = facultes['labels'].apply(lambda x: renameLongLabels(x))
facultes = facultes.rename(columns={'labels':'Faculté', 'count':'N'})

figFacultes = px.pie(
    facultes, 
    values= 'N',
    labels = 'Faculté', 
    names= 'Faculté', 
    title='Nombre de professeur-e-s par faculté',
    hover_name = "Faculté",
    hole=0.6 
)

figFacultes = figFacultes.update_traces(
    textposition='inside')

figFacultes = figFacultes.update_layout(
    uniformtext_minsize=12, 
    uniformtext_mode='hide',
    legend=dict(font=dict(size= 12)),
    margin = dict(l=20)    
)

# Nombre de professeurs par établissement affilié
# Table
def groupEtablissements(etablissementNom : str) -> str : 
   return etablissementNom.split(' – ')[0]

# Etablissements affiliés
etablissementsAffilies = expertises.dropna(subset='etablissementsAffilies.nom')
etablissementsAffilies = etablissementsAffilies.drop_duplicates(subset=(['idsadvr', 'etablissementsAffilies.nom']))
etablissementsAffilies.loc[:, 'etablissementsAffilies.nom'] = etablissementsAffilies['etablissementsAffilies.nom'].apply(
    lambda x : x.split(' – ')[0])
etablissementsAffilies = pd.DataFrame(
    plotVariable(etablissementsAffilies, 'etablissementsAffilies.nom')
    ).sort_values(by='count', ascending = False)

etablissementsAffilies = etablissementsAffilies.rename(
    columns={
        'labels':'Établissement', 
        'count':'N'
    }
)

# Secteurs
etablissementsAffilies['noms'] = etablissementsAffilies['Établissement'].apply(lambda x: renameLongLabels(x))
figEtablissementsAffilies = px.pie(
    etablissementsAffilies,
    labels = etablissementsAffilies['Établissement'],
    names = etablissementsAffilies['noms'],
    values = etablissementsAffilies['N'],
    title = 'Nombre de professeurs par établissement affilié',
    hover_name = "Établissement",
    hole = 0.6
)

figEtablissementsAffilies = figEtablissementsAffilies.update_traces(
    textposition='inside')

figEtablissementsAffilies = figEtablissementsAffilies.update_layout(
    uniformtext_minsize=12, 
    uniformtext_mode='hide',
    legend=dict(font=dict(size= 12)),
    margin=dict(l=20)    
)

# Nombre de professeur par département
departements = pd.DataFrame(plotVariable(expertises, 'affiliations.departement.nom'))
departements = departements.rename(columns={'labels':'Département', 'count':'N'})

departements['noms'] = departements['Département'].apply(lambda x: renameLongLabels(x))
figDepartements = px.bar(
    departements.sort_values(by='N'),
    y = 'noms',
    x = 'N',
    title = 'Nombre de professeur-e-s par département',
    orientation = 'h',
    hover_name = "Département",
    hover_data = ['Département', 'N'],
    height = 2000
)

# Adjust the bar width and spacing
figDepartements.update_traces(
    width = 0.6  # Set the bar width
)

# Hide axis names (labels)
figDepartements.update_layout(
    title_x=0.01, # Move title to the left
    xaxis_title=None,  # Hide x-axis title
    yaxis_title=None,   # Hide y-axis title
    legend=dict(font=dict(size= 12)),
    margin=dict(b=0, l=60, t=30)
)

# Principales disicplines de recherche 
disciplines = expertises[[
    'idsadvr', 'expertise.disciplines.nom', 
    'expertise.disciplines.uid', 'expertise.disciplines.codeLangue'
]].dropna(subset='expertise.disciplines.uid').drop_duplicates()

disciplines = disciplines.groupby([
    'expertise.disciplines.nom', 
    'expertise.disciplines.uid', 
    'expertise.disciplines.codeLangue'
    ])['idsadvr'].count().reset_index().rename(columns={'idsadvr': 'count'})

disciplines = disciplines.sort_values(by=['expertise.disciplines.uid', 'expertise.disciplines.codeLangue'], ascending=[True, False])
disciplines = disciplines.drop_duplicates(subset='expertise.disciplines.uid', keep='first').sort_values(by='count', ascending=False)

disciplines = disciplines[['expertise.disciplines.nom', 'count']]
tableDisciplines = disciplines.rename(columns={'expertise.disciplines.nom':'Discipline', 'count':'N'})

# Dropdown: principales disciplines de recherche par faculté
mappingDisciplines = pd.read_csv('tables/SADVR_disciplines.csv')
mappingDisciplines = mappingDisciplines[mappingDisciplines['noms.codeLangue'] == 'fre']
mappingDisciplines = {str(x['id']): x['noms.nom'] for x in mappingDisciplines.to_dict('records')}

disciplines = expertises[
    ['idsadvr', 
    'affiliations.faculte.nom', 
    'expertise.disciplines.uid']
].dropna(subset='expertise.disciplines.uid').drop_duplicates()

disciplines['expertise.disciplines.nom'] = disciplines['expertise.disciplines.uid'].astype(str).map(mappingDisciplines)
disciplines = disciplines.drop(columns='expertise.disciplines.uid')

mappingDisciplines = pd.read_csv('tables/SADVR_disciplines.csv')
mappingDisciplines = mappingDisciplines[mappingDisciplines['noms.codeLangue'] == 'fre']
mappingDisciplines = {str(x['id']): x['noms.nom'] for x in mappingDisciplines.to_dict('records')}


# Group by 'faculty' and 'discipline' and count the number of professors in each group
faculty_discipline_counts = disciplines.groupby(['affiliations.faculte.nom', 'expertise.disciplines.nom'])['idsadvr'].count().reset_index()

# Rename the 'id' column to 'professor_count' for clarity
faculty_discipline_counts = faculty_discipline_counts.rename(
    columns={
        'idsadvr': 'count', 
        'affiliations.faculte.nom' : 'Faculté',
        'expertise.disciplines.nom': 'Discipline'
    }
)

faculty_discipline_counts = faculty_discipline_counts.sort_values(by='count', ascending=False)
faculty_discipline_counts['noms'] = faculty_discipline_counts['Discipline'].apply(renameLongLabels)

def generate_pie_chart(selected_faculty):
    filtered_df = faculty_discipline_counts[faculty_discipline_counts['Faculté'] == selected_faculty].dropna()

    # Extraire les dix principales disciplines associées à une faculté
    filtered_df = filtered_df.sort_values(by='count', ascending=False)
    if(len(filtered_df) > 10):
        filtered_df = groupOtherValues(filtered_df, 10)[:10]
    fig = px.pie(
        filtered_df,
        hover_name = 'Discipline', 
        names = 'noms',
        values = 'count',
        hole = 0.6,
    )

    fig.update_layout(margin=dict(l=0, r=70, t=10, b=10))


    return fig

# Create a figure for each category
disciplinesFacultes = {}
for faculte in faculty_discipline_counts['Faculté'].unique():
    fileName = f'figures/disciplinesFaculte/{slugify(faculte)}.html'
    with open(fileName, 'w', encoding='utf-8') as f:
        f.write(generate_pie_chart(faculte).to_html(full_html=False, include_plotlyjs='cdn'))

    disciplinesFacultes[faculte] = "../"+fileName

# Cartographie des expertises de recherche: mots-clés associés aux principales disciplines de recherche de l'UdeM 
## Extraire les fréquences associées aux disciplines et aux mots-clés: elles vont permettre d'assigner
# une taille aux noeuds dans le graphe (plus fréquent = plus gros )
def freqVariable(variable: str, df: pd.DataFrame = motsCles) -> pd.DataFrame:
    output = df[[
        'idsadvr',
        f'expertise.{variable}.nom', 
        f'expertise.{variable}.uid']
    ].dropna(subset=f'expertise.{variable}.uid').drop_duplicates()

    output = output.groupby([f'expertise.{variable}.nom', f'expertise.{variable}.uid'])['idsadvr'].count().reset_index()
    output = output.rename(columns={'idsadvr': 'count'})
    output = output[[f'expertise.{variable}.nom', 'count']]

    return output

listeDepartements = [x for x in motsCles['département'].unique().tolist() if 
    ((not "Direction" in x) and 
    (not "Bureau" in x) and 
    (not "Dir" in x) and 
    (not "rectorat" in x) and
    (not "recteur" in x))
]

graphs = []
tablesGraphs = {}
mappingTables = {
    'expertise.disciplines.nom': 'Discipline',
    'expertise.motsCles.nom': 'Mot-Clé',
    'freqMotCle': 'N'
}

tableClasses = ['table', 'table-hover']

for departement in listeDepartements:
    nx_graph = nx.Graph()
    subdf = motsCles[motsCles['département'] == departement].dropna()

    # Disciplines
    freqDisciplines = freqVariable('disciplines', subdf)
    freqDisciplines = {x['expertise.disciplines.nom'] : x['count'] for x in freqDisciplines.to_dict('records')}

    # Mots-clés
    freqMotsCles = freqVariable('motsCles', subdf)
    freqMotsCles = {x['expertise.motsCles.nom'] : x['count'] for x in freqMotsCles.to_dict('records')}

    subdf['freqDiscipline'] = subdf['expertise.disciplines.nom'].map(freqDisciplines)
    subdf['freqMotCle'] = subdf['expertise.motsCles.nom'].map(freqMotsCles)
    topMotsCles = subdf[['expertise.motsCles.nom','freqMotCle']].drop_duplicates()
    topMotsCles = topMotsCles.sort_values(by='freqMotCle', ascending=False)[:15]['expertise.motsCles.nom'].tolist()

    subdf = subdf[subdf['expertise.motsCles.nom'].isin(topMotsCles)]

    subdf = subdf[['département', 'expertise.disciplines.nom', 'freqDiscipline', 'expertise.motsCles.nom', 'freqMotCle']]

    records = (subdf.sort_values(by='freqMotCle', ascending=False).to_dict('records'))
    recordsD = (pd.DataFrame(records).drop_duplicates(subset='expertise.disciplines.nom')).to_dict('records')

    # Noeuds pour les disciplines
    tuples = [
        (r['expertise.disciplines.nom'], 
        {"color": "#0b113a", 
         "shape": "square", 
         "size": 1+(10*math.log(int(r['freqDiscipline']))),
         "n": int(r['freqDiscipline'])
         }) for r in recordsD]
    
    sizes = [r['freqDiscipline'] for r in recordsD]

    # Noeuds pour les mots-clés
    tuples += [
        (r['expertise.motsCles.nom'], 
        {"color": "#ffca40",
         "shape": "dot",
         "size": 1+(15*math.log(int(r['freqMotCle']))),
         "n": int(r['freqMotCle'])
        }) for r in records]

    sizes += [r['freqMotCle'] for r in records]

    # Liens 
    edges = [(r['expertise.disciplines.nom'], r['expertise.motsCles.nom']) for r in records]

    nx_graph.add_nodes_from(tuples)
    nx_graph.add_edges_from(edges)

    # Set node attributes (colors)
    nx.set_node_attributes(nx_graph, {node: attr_dict for node, attr_dict in tuples})

    # Create a Pyvis Network instance
    pyvis_graph = Network(notebook=True, height="575px", width="100%", cdn_resources='remote')

    # Add nodes and edges to Pyvis Network
    for node, attr in nx_graph.nodes(data=True):
        pyvis_graph.add_node(
            node, 
            shape= attr['shape'],
            color=attr['color'], 
            size=  attr['size'], 
            font= {'size': 70},
            title=f"{node}\nN={attr['n']}",
            )


    for edge in nx_graph.edges():
        pyvis_graph.add_edge(edge[0], edge[1], color='lightgrey')

    # Set layout to forceAtlas2Based for better node spacing
    pyvis_graph.barnes_hut(gravity=-9000, central_gravity=0.3, spring_length=50)
    # pyvis_graph.show_buttons(filter_=['physics'])
    pyvis_graph.set_options(
        """
        const options = {
        "physics": {
            "barnesHut": {
            "theta": 0.75,
            "gravitationalConstant": -30000,
            "centralGravity": 1.1,
            "springLength": 50,
            "springConstant": 0.001
            },
            "maxVelocity": 61,
            "minVelocity": 0.01,
            "timestep": 0.67
            }
        }
        """)

    # Save the graph to an HTML file
    name = slugify(departement)
    output_html = f"figures/graphs/graph__{name}.html"

    graphs.append({"Département": departement, "Fichier": f"../{output_html}"})
    pyvis_graph.show(output_html) 

    # Create the table to display aside from the graph
    tableG = subdf.rename(columns = mappingTables)
    tableG = tableG.drop(columns = ['département'])
    tableG = tableG.groupby(['Discipline','Mot-Clé']).max() 

    # tableG = tableG.drop_duplicates()
    tableG = tableG.sort_values(by=["freqDiscipline", 'N'], ascending=[False, False])
    tableG = tableG.drop(columns="freqDiscipline")

    tablesGraphs[f"../{output_html}"] = tableG.to_html(classes = tableClasses, justify='left')

    # Réinitialiser le graphe
    nx_graph.clear()

tablesGraphs = str(tablesGraphs)

