from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from utils.SADVR_utils import *

### Build tables
# Charger les données
data = updateInfoProfs()
demographics = data[['idsadvr', 'sexe', 'langues', 'formations', 'affiliations']]
# Normalisation - données demographiques
fonctionsProf = pd.read_csv('utils/fonctionsProfs.csv')['codeSad'].tolist()
toNormalize = ['langues', 'affiliations', 'formations', 'formations.disciplines', 'formations.institutions']
for c in toNormalize:
    demographics = explodeNormalize(demographics, c)

columns = pd.read_csv('utils/columnsDemographics.csv')['columns'].tolist()
demographics = demographics[[x for x in demographics.columns if x in columns]]

demographics = demographics[demographics['affiliations.fonction.codeSad'].isin(fonctionsProf)]
demographics.to_csv('tables/demographics.csv', index=False)


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

# nbEtablissementsAffilies = 27

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
    hole=0.5,
    title='Identité de genre',
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
    hole=0.5,
    width=600, 
    category_orders= {'labels':
        order
    }
)

# Année d'obtention du dernier diplôme - selon le genre
# D'abord filtrer pour ne conserver que le dernier diplôme obtenu
anneeDiplome = demographics.sort_values(['idsadvr', 'formations.annee'], ascending=[True, False])
anneeDiplome = anneeDiplome[['idsadvr', 'sexe', 'formations.annee']].dropna(subset='formations.annee')
anneeDiplome = anneeDiplome.drop_duplicates(subset=['idsadvr', 'formations.annee'])

anneeDiplomeGenre =  pd.DataFrame(
    anneeDiplome.drop(columns='idsadvr').value_counts()
    ).reset_index().sort_values(by='formations.annee', ascending=True)

figAnneDiplomeGenre = px.line(
    anneeDiplomeGenre, 
    x = 'formations.annee', 
    y = 'count',
    color = 'sexe',
    title = "Année d'obtention du dernier diplôme selon le genre",
    width=900,
    line_shape = 'spline')

# Rang professoral par genre
fonctionGenre = demographics[['idsadvr', 'sexe', 'affiliations.fonction.codeSad']].drop_duplicates()
freqFonctionGenre = pd.DataFrame(fonctionGenre[['sexe', 'affiliations.fonction.codeSad']].value_counts()).reset_index()

mapping = pd.read_csv('tables/SADVR_fonctions.csv')[['codeSad', 'nomM']].to_dict('records')
mapping = {x['codeSad'] : x['nomM'] for x in mapping}

freqFonctionGenre['fonction'] = freqFonctionGenre['affiliations.fonction.codeSad'].map(mapping)
freqFonctionGenre.to_csv('tables/statistiques__sociodemographiques/fonctionGenre.csv', index=False)

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
    hole=0.5,
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
    hole=0.5,
    category_orders={'labels': order},
)

# Pays de formation - représentation géographique
# Passer du code iso-2 à iso-3 pour que ce soit conforme à ce qu'attent Plotly
mappingIso = pd.read_csv('utils/mappingPays_iso.csv', sep=';').to_dict('records')
mappingIso = {x['Alpha-2 code'] : x['Alpha-3 code'] for x in mappingIso}

# Dresser le mapping entre les codes iso-2 aux noms de pays
mappingNomsPays = (
    demographics[['formations.institutions.paysNom', 'formations.institutions.paysCode']].drop_duplicates()
    ).to_dict('records')

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
    
#### Create the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    children = [html.H1
        (
            "SADVR - Portrait statistique",
            style = {
                'textAlign': 'center',
                'color': 'white', 
                'backgroundColor': '#0b113a',
                'padding': '30px',
                'fontFamily': 'Calibri'
                }
        ),
        
        html.Div(
            style = {
                'border' : '1px solid lightgrey',
                'paddingTop': '2%',
                'marginBottom': '2%',
                'marginLeft': '10%',
                'marginRight': '10%',
                'paddingLeft': '5%',
                'paddingRight': '5%',
                'boxShadow': shadow
            }, 
            children= [
                # Titre de l'onglet
                html.H2(
                    'Professeur·e·s - Portrait sociodémographique', 
                    style={
                            'textAlign': 'left',
                            'color': '#444444',
                    }
                ),

                # Trait de soulignement
                html.Hr(
                    style={
                        'borderTop': '4px solid #52B782',
                        'width' : '50%',
                        'marginBottom': '50px'
                    }
                ),

                # Cartes
                html.Div(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    cardNbProfs,
                                    width = 6,
                                    lg = 3  
                                ),
                                dbc.Col(
                                    cardNbFacultes,
                                    width = 6,
                                    lg = 3   
                                ),
                                dbc.Col(
                                    cardNbDepartements,
                                    width = 6,
                                    lg = 3  
                                ),
                                
                                dbc.Col(
                                    cardNbEtablissementsAffilies, 
                                    width = 6,
                                    lg = 3  
                                ),
                            ]
                        )
                    ]
                ),

                # Trait de soulignement
                html.Hr(
                    style={
                        'borderTop': '1px solid #lightgrey',
                        'marginTop': '50px',
                        'marginBottom': '50px'
                    }
                ),

                # Secteurs - genre + pays d'obtention du dernier diplôme
                html.Div(
                    [dbc.Row
                        (
                            [
                                dbc.Col(
                                    dcc.Graph(figure=figGenre),
                                    width = 6,
                                ),
                                dbc.Col(
                                    dcc.Graph(figure=figPaysDiplome),
                                    width = 6,
                                )
                            ]
                        ), 
                    ],
                ),

                # Trait de soulignement
                html.Hr(
                    style={
                        'borderTop': '1px solid #lightgrey',
                        'marginBottom': '30px'
                    }
                ),

                # Courbe - Année d'obtention du dernier diplôme - par genre
                html.Div(
                    children = [dcc.Graph(figure=figAnneDiplomeGenre)]
                ),

                # Trait de soulignement
                html.Hr(
                    style={
                        'borderTop': '1px solid #lightgrey',
                        'marginBottom': '30px',
                         'marginTop': '30px'
                    }
                ),

                # Barres - Rang professoral par genre
                html.Div(
                    style = {
                        'marginLeft':'-50px', 
                        'maxHeight': '450px', 
                        'overflow-y': 'scroll'},
                    children = [dcc.Graph(figure = figFonctionGenre)]
                ),

                # Trait de soulignement
                html.Hr(
                    style={
                        'borderTop': '1px solid #lightgrey',
                        'marginBottom': '30px'
                    }
                ),

                # Pays de formation - représentation géographique 
                html.Div(
                    style = {
                        'marginLeft' : '-20px'
                    },
                    children =  [dcc.Graph(figure=figPaysFormation)]
                ),

                # Trait de soulignement
                html.Hr(
                    style={
                        'borderTop': '1px solid #lightgrey',
                        'marginBottom': '30px'
                    }
                ),

                # Langues écrites et parlées 
                html.Div(
                    [dbc.Row
                        (
                            [
                                dbc.Col(
                                    dcc.Graph(figure= figLanguesParlees),
                                    width = 6,
                                ),
                                dbc.Col(
                                    dcc.Graph(figure= figLanguesEcrites),
                                    width = 6,
                                )
                            ]
                        ), 
                    ],
                ),
            ],
        )
    ]
)

if __name__ == '__main__':
    app.run(debug=True, port=2223)