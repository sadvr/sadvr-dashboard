from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(
    children=[
        html.H1('SADVR - Portrait statistique', style={
            'textAlign': 'center', 
            'color': 'white', 
            'background-color': '#0b113a',
            'padding': '20px',
            'font-family': 'Calibri'}),

        html.Div(style={'width': '450px', 'padding-left': '20px'} ,children= [
            html.H2('Professeur·e·s - Portrait sociodémographique', 
                style={
                    'textAlign': 'left',
                    'color': '#444444',
                    'font-family': 'Calibri',
                }
            ),

            html.Hr(
                style={
                    'border-top': '2px solid #52B782'
                }
            )
        ]), 

        dcc.Graph(
            id='example-graph',
            figure=fig
        )
    ]
)

if __name__ == '__main__':
    app.run(debug=True)
