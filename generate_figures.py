from utils.sadvr_utils import *
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dash_table
import plotly.express as px
import plotly.graph_objects as go

# Charger les données
data = updateInfoProfs()

### Analyses sociodémographiques
demographics = data[['idsadvr', 'sexe', 'langues', 'formations', 'affiliations']]

# Normalisation - données demographiques
fonctionsProf = pd.read_csv('utils/fonctionsProfs.csv')['codeSad'].tolist()
toNormalize = ['langues', 'affiliations', 'formations', 'formations.disciplines', 'formations.institutions']
for c in toNormalize:
    demographics = explodeNormalize(demographics, c)

columns = pd.read_csv('utils/columnsDemographics.csv')['columns'].tolist()
demographics = demographics[[x for x in demographics.columns if x in columns]]

demographics = demographics[demographics['affiliations.fonction.codeSad'].isin(fonctionsProf)]

### 1e visuel : 4 mesures "Count"
# 1: nombre de professeurs
nbProfs = len(data.drop_duplicates(subset='idsadvr'))

# Visuel : card
cardNbProfs = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4(str(nbProfs), className="card-title"),
                html.P("Professeur·e·s",
                    className="card-text",
                ),
            ],
            style={'textAlign':'center'}
        ),
    ],
)


# 2: nombre de facultés et écoles
nbFacultes = len(getTable('facultes'))
# Visuel : card
cardNbFacultes = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4(str(nbFacultes), className="card-title"),
                html.P("Facultés et écoles",
                    className="card-text",
                ),
            ],
            style={'textAlign':'center'}
        ),
    ]
)

# 3: nombre de départements
nbDepartements = len(getTable('departements'))

# Visuel : card
cardNbDepartements = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4(str(nbDepartements), className="card-title"),
                html.P("Départements",
                    className="card-text")
            ],
            style={'textAlign':'center'}
        ),
    ],
)

# 4: Nombre d'établissements affiliés
etablissementsAffilies = data[['idsadvr', 'etablissementsAffilies']]
etablissementsAffilies = explodeNormalize(etablissementsAffilies, 'etablissementsAffilies')
etablissementsAffilies = etablissementsAffilies.dropna(subset='etablissementsAffilies.nom')
etablissementsAffilies = etablissementsAffilies.drop_duplicates(subset=(['idsadvr', 'etablissementsAffilies.nom']))
etablissementsAffilies = pd.DataFrame(plotVariable(etablissementsAffilies, 'etablissementsAffilies.nom'))
nbEtablissementsAffilies = len(etablissementsAffilies)

# Visuel: Card
cardNbEtablissementsAffilies = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4(str(nbEtablissementsAffilies), className="card-title"),
                html.P("Établissements affiliés",
                    className="card-text")
            ],
            style={'textAlign':'center'}
        ),
    ],
)

# Visuel "Cartes" - style
shadow = '2px 2px 6px lightgrey'

# Genre
mapping = {'M': 'Hommes', 'F': 'Femmes', 'A': 'Autres'}
genre = plotVariable(demographics, 'sexe', mapping=mapping)

figGenre = px.pie(
    names = genre['labels'],
    values = genre['count'],
    hole=0.6,
    title='Identité de genre',
)

figGenre.update_layout(
    legend=dict(font=dict(size= 11)),
    margin=dict(l=0)
)

# Pays d'obtention du dernier diplôme
paysFormation = pd.DataFrame(plotVariable(demographics, 'formations.institutions.paysNom'))
paysFormation = groupOtherValues(paysFormation, 8)

order = [x for x in paysFormation['labels'] if not (x == 'Autre')] + ['Autre']

figPaysDiplome = px.pie(
    paysFormation, 
    values= paysFormation['count'], 
    names= paysFormation['labels'], 
    title="Lieu d'obtention du dernier diplôme",
    hole=0.6,
    width=600, 
    category_orders= {'labels':
        order
    }
)

figPaysDiplome.update_traces(
    textposition='inside')

figPaysDiplome.update_layout(
    uniformtext_minsize=12, 
    uniformtext_mode='hide',
    legend=dict(font=dict(size= 11)),
    margin=dict(l=0)
)

# Année d'obtention du dernier diplôme - selon le genre
# D'abord filtrer pour ne conserver que le dernier diplôme obtenu
anneeDiplome = demographics.sort_values(['idsadvr', 'formations.annee'], ascending=[True, False])
anneeDiplome = anneeDiplome[['idsadvr', 'sexe', 'formations.annee']].dropna(subset='formations.annee')
anneeDiplome = anneeDiplome.drop_duplicates(subset=['idsadvr', 'formations.annee'])

anneeDiplomeGenre =  pd.DataFrame(anneeDiplome.drop(columns='idsadvr').value_counts()).reset_index().sort_values(by='formations.annee', ascending=True)

figAnneDiplomeGenre = px.line(
    anneeDiplomeGenre, 
    x = 'formations.annee', 
    y = 'count',
    color = 'sexe',
    title = "Année d'obtention du dernier diplôme selon le genre",
    width=900,
    line_shape = 'spline')

#figAnneDiplomeGenre.update_traces(mode="markers+lines", hovertemplate=None)
figAnneDiplomeGenre.update_layout(
    hovermode="x unified"
)

# Rang professoral par genre
fonctionGenre = demographics[['idsadvr', 'sexe', 'affiliations.fonction.codeSad']].drop_duplicates()
freqFonctionGenre = pd.DataFrame(fonctionGenre[['sexe', 'affiliations.fonction.codeSad']].value_counts()).reset_index()

mapping = pd.read_csv('tables/SADVR_fonctions.csv')[['codeSad', 'nomM']].to_dict('records')
mapping = {x['codeSad'] : x['nomM'] for x in mapping}

freqFonctionGenre['fonction'] = freqFonctionGenre['affiliations.fonction.codeSad'].map(mapping)

freqFonctionGenre = freqFonctionGenre[['sexe', 'fonction', 'count']]
freqFonctionGenre = freqFonctionGenre[freqFonctionGenre['sexe'] != 'A']
freqFonctionGenre = freqFonctionGenre[freqFonctionGenre['fonction'] != 'Professeur de formation pratique titulaire'] # anomalie
freqFonctionGenre = freqFonctionGenre.sort_values(by='count', ascending=True)
freqFonctionGenre

figFonctionGenre = px.bar(
    freqFonctionGenre,
    y = 'fonction',
    x = 'count',
    title = 'Rang professoral par genre',
    color = 'sexe',
    barmode='group',
    height=900,
    orientation = 'h',
)

figFonctionGenre.update_layout(
     yaxis_title=None,
     xaxis_title=None
)

# Langues parlées
langueParle = demographics[demographics['langues.medium'] == 'Oral'].drop(columns=['langues.medium'])
langueParle = pd.DataFrame(plotVariable(langueParle, 'langues.nom'))
langueParle = groupOtherValues(langueParle)

figLanguesParlees = px.pie(
    langueParle,
    values = langueParle['count'], 
    names = langueParle['labels'], 
    title='Langues parlées',
    hole=0.6,
    category_orders={'langues.nom': 
        ['Français', 'Anglais', 'Espagnol; castillan', 
         'Allemand', 'Italien', 'Arabe', 'Autre']},
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
mappingNomsPays = (demographics[['formations.institutions.paysNom', 'formations.institutions.paysCode']].drop_duplicates()).to_dict('records')
mappingNomsPays = {x['formations.institutions.paysCode'] : x['formations.institutions.paysNom'] for x in mappingNomsPays}

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
    projection = 'equirectangular',
    
)

# Customize the layout
figPaysFormation.update_geos(
    showcoastlines=False,  # Hide coastlines/borders
    showland=True,  # Hide land area color
    landcolor = '#E8E8E8',
    showframe=False,  # Hide frame/borders
    projection_scale = 1.2,  # Adjust the projection scale to fit the map better
    center=dict(lon=10, lat=18),  # Set the center of the map to exclude Antarctica
)

figPaysFormation = figPaysFormation.update_layout( 
    title = "Formation - Pays d'obtention du dernier diplôme",
    margin=dict(t=40, l=60), 
    height = 600
)

### Analyses expertises de recherche
# Éléments de visuel
shadow = '2px 2px 6px lightgrey'

expertises = data[['idsadvr', 'affiliations', 'etablissementsAffilies', 'expertise']]

toNormalize = [
    'affiliations',
    'etablissementsAffilies',
    'expertise',
    'expertise.secteursRecherche',
    'expertise.disciplines',
    'expertise.pays',
    'expertise.continents',
    'expertise.periodesChronologiques'
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
# Fin zone commentée

#### Construire les tables et les figures à inclure dans le board
# Nombre de professeurs par faculté
facultes = pd.DataFrame(plotVariable(expertises, 'affiliations.faculte.nom'))[:-2].sort_values(by='count', ascending=False)

# Table 
tableFacultes = dash_table.DataTable(
    data = facultes.to_dict('records'), 
    columns = [{"name": i, "id": i} for i in facultes.columns],
    style_data={
        'whiteSpace': 'normal',
        'height' : 'auto',
    },

    style_table = {
        'height' : 'auto',
        'maxHeight': '450px',
        'overflowY': 'scroll',
    },

    style_cell={
        'textAlign': 'left',
        'fontFamily': 'Calibri'} # left align text in columns for readability
)


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
etablissementsAffilies.loc[:, 'etablissementsAffilies.nom'] = etablissementsAffilies['etablissementsAffilies.nom'].apply(lambda x : x.split(' – ')[0])
etablissementsAffilies = pd.DataFrame(plotVariable(etablissementsAffilies, 'etablissementsAffilies.nom')).sort_values(by='count', ascending = False)
etablissementsAffilies = etablissementsAffilies.rename(columns={'labels':'Établissement', 'count':'N'})

tableEtablissements = dash_table.DataTable(
    data = etablissementsAffilies.to_dict('records'), 
    columns = [{"name": i, "id": i} for i in etablissementsAffilies.columns],
    style_data={
        'whiteSpace': 'normal',
        'height' : 'auto',
    },

    style_table = {
        'height': '450px',
        'overflowY': 'scroll',
    },

    style_cell={
        'textAlign': 'left',
        'fontFamily': 'Calibri'} # left align text in columns for readability
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
# Table
departements = pd.DataFrame(plotVariable(expertises, 'affiliations.departement.nom'))
departements = departements.rename(columns={'labels':'Département', 'count':'N'})

# Barres 



departements['noms'] = departements['Département'].apply(lambda x: renameLongLabels(x))
figDepartements = px.bar(
    departements.sort_values(by='N'),
    y = 'noms',
    x = 'N',
    title = 'Nombre de professeur-e-s par département',
    orientation = 'h',
    hover_name = "Département",
    hover_data = ['Département', 'N'],
    height = 1200
)

# Adjust the bar width and spacing
figDepartements.update_traces(
    width = 0.6  # Set the bar width (0.8 is the default, adjust as needed)
)

# Hide axis names (labels)
figDepartements.update_layout(
    xaxis_title=None,  # Hide x-axis title
    yaxis_title=None,   # Hide y-axis title
    legend=dict(font=dict(size= 12))
)

# Principales disicplines de recherche à l'UdeM (Top 30)
disciplines = expertises[[
    'idsadvr', 'expertise.disciplines.nom', 
    'expertise.disciplines.uid', 'expertise.disciplines.codeLangue'
]].dropna(subset='expertise.disciplines.uid').drop_duplicates()

disciplines = disciplines.groupby(['expertise.disciplines.nom', 'expertise.disciplines.uid', 
                    'expertise.disciplines.codeLangue'])['idsadvr'].count().reset_index().rename(columns={'idsadvr': 'count'})

disciplines = disciplines.sort_values(by=['expertise.disciplines.uid', 'expertise.disciplines.codeLangue'], ascending=[True, False])
disciplines = disciplines.drop_duplicates(subset='expertise.disciplines.uid', keep='first').sort_values(by='count', ascending=False)

disciplines = disciplines[['expertise.disciplines.nom', 'count']]
tableDisciplines = disciplines.rename(columns={'expertise.disciplines.nom':'Discipline', 'count':'N'})

# disciplines = groupOtherValues(disciplines, 30)[:30]
# figDisciplines = go.Figure(
#     go.Treemap(
#         labels= disciplines['expertise.disciplines.nom'],
#         parents= [''] * len(disciplines),
#         values = disciplines['count'],
#     )
# )

# figDisciplines = figDisciplines.update_layout(
#     height = 600,
#     margin = dict(t=20, l=20, b=50)
# )


# Dropdown: principales disciplines de recherche par faculté
mappingDisciplines = pd.read_csv('tables/SADVR_disciplines.csv')
mappingDisciplines = mappingDisciplines[mappingDisciplines['noms.codeLangue'] == 'fre']
mappingDisciplines = {str(x['id']): x['noms.nom'] for x in mappingDisciplines.to_dict('records')}

disciplines = expertises[
    ['idsadvr', 'affiliations.faculte.nom', 'expertise.disciplines.uid']
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
    columns={'idsadvr': 'count', 'affiliations.faculte.nom' : 'Faculté', 'expertise.disciplines.nom': 'Discipline'})
faculty_discipline_counts = faculty_discipline_counts.sort_values(by='count', ascending=False)
faculty_discipline_counts['noms'] = faculty_discipline_counts['Discipline'].apply(renameLongLabels)

def generate_pie_chart(selected_faculty):
    filtered_df = faculty_discipline_counts[faculty_discipline_counts['Faculté'] == selected_faculty]

    # Extraire les dix principales disciplines associées à une faculté
    filtered_df = filtered_df.sort_values(by='count', ascending=False)
    filtered_df = groupOtherValues(filtered_df, 6)[:6]
    fig = go.Figure(go.Pie(
        labels= filtered_df['Discipline'], 
        # names = filtered_df['noms'],
        values = filtered_df['count'],
        hole = 0.6)
    )
    return fig

# Create a figure for each category
figs = {
    c: generate_pie_chart(c).update_traces(name=c, visible=False)
    for c in faculty_discipline_counts['Faculté'].unique()
}

fig = go.Figure(
    layout=go.Layout(
        title=go.layout.Title(text="Principales disciplines de recherche par faculté")
    )
)

# Default category
defaultcat = faculty_discipline_counts['Faculté'].unique()[0]
fig.add_traces(
    figs[defaultcat].data
    ).update_traces(visible=True)

# integrate figures per category into one figure
for k in figs.keys():
    if k != defaultcat:
        fig.add_traces(figs[k].data)

fig.update_layout(height=445)
fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
fig.update_layout(legend=dict(yanchor="bottom",y=0,xanchor="left", x=-1))

# finally build dropdown menu
fig.update_layout(
    title_x=0.02,  # Adjust this value to move the title to the left,
    updatemenus=[
        {
            "buttons": [
                {
                    "label": k,
                    "method": "update",
                    
                    # list comprehension for which traces are visible
                    "args": [{"visible": [kk == k for kk in figs.keys()]}],
                }
                for k in figs.keys()
            ]
        }
    ],
    
)


figDisciplinesFacultes = fig

# Cartographie des expertises de recherche: mots-clés associés aux principales disciplines de recherche de l'UdeM 