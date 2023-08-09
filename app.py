from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from utils.SADVR_utils import *


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Éléments de visuel
shadow = '2px 2px 6px lightgrey'

# Commennter à partir d'ici
### Charger les données
data = updateInfoProfs()

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
facultes = pd.DataFrame(plotVariable(expertises, 'affiliations.faculte.nom'))[:-2].sort_values(by='count')
figFacultes = px.pie(
    facultes, 
    values= 'count', 
    names= 'labels', 
    title='Nombre de professeur-e-s par facultés',
    hole=0.5 
)

# Nombre de professeurs par établissements affiliés
def groupEtablissements(etablissementNom : str) -> str : 
   return etablissementNom.split(' – ')[0]

# Etablissements affiliés
etablissementsAffilies = expertises.dropna(subset='etablissementsAffilies.nom')
etablissementsAffilies = etablissementsAffilies.drop_duplicates(
    subset=(['idsadvr', 'etablissementsAffilies.nom']))
etablissementsAffilies.loc[:, 'etablissementsAffilies.nom'] = etablissementsAffilies['etablissementsAffilies.nom'].apply(lambda x : x.split(' – ')[0])
etablissementsAffilies = pd.DataFrame(plotVariable(etablissementsAffilies, 'etablissementsAffilies.nom')).sort_values(by='count', ascending = True)

figEtablissementsAffilies = px.pie(
    etablissementsAffilies,
    names = 'labels',
    values = 'count',
    hole=0.5,
    title='Nombre de professeur-e-s par établissement affilié',
)

# Disciplines de recherche (top 30)


# Dropdown: principales disciplines de recherche par faculté


# Dropdown: principales disciplines de recherche par département


# Dropdown: principales disicplines de recherche selon le genre ?


# Nombre d'unités de recherche par faculté


# Nombre d'unités de recherche par département


# Cartographie des expertises de recherche: mots-clés associés aux principales disciplines de recherche de l'UdeM


## App Layout 
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
                'marginLeft': '7%',
                'marginRight': '7%',
                'paddingLeft': '3%',
                'paddingRight': '3%',
                'boxShadow': shadow
            }, 
            children= [
                # Titre de l'onglet
                html.H2(
                    'Expertises de recherche', 
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

                # Secteurs - genre + pays d'obtention du dernier diplôme
                html.Div(
                    [dbc.Row
                        (
                            [
                                dbc.Col(
                                    dcc.Graph(figure=figFacultes),
                                    width = 6,
                                ),
                                dbc.Col(
                                    dcc.Graph(figure=figEtablissementsAffilies),
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

            ],
        )
    ]
)

if __name__ == '__main__':
    app.run(debug=True, port=8051)
