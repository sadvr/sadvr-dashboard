from dash import Dash, html, dcc
import plotly.io as pio
import dash_bootstrap_components as dbc
from utils.SADVR_utils import *
from generateFigures import *

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

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
    app.run(debug=True, port=8050)
