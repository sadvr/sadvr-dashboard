from dash import Dash, html, dcc, dash_table
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from utils.sadvr_utils import *
from generate_figures import *

# utils to generate html file
tableClasses = ['table', 'table-bordered', 'table-hover', 'table-sm']

with open('./html/header.html', encoding='utf-8') as f:
    header = f.read()

with open('./html/footer.html') as f:
    footer = f.read()

### Générer le fichier html pour les professeurs



### Générer le fichier html pour les affiliations
with open('html/affiliations.html', 'w', encoding='utf-8') as f:
    f.write(header)
    f.write('<h2>Affiliations</h2></div>')

    # Établissements affiliés
    f.write('<h3>Établissements affiliés</h3>')
    f.write(
        """
        <div class="grid">
            <div class="col-md-4" 
                style="float:left; padding-right:5px; 
                margin-top:10px; max-height:425px; overflow-y:scroll;">
        """
    )

    f.write(etablissementsAffilies[['Établissement', 'N']].to_html(
        index=False, classes=tableClasses, justify='left')
    )

    f.write('</div><div class="col-md-8" style="float:right; padding-right:20px;">')
    f.write(figEtablissementsAffilies.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('</div></div>')
    f.write('<div style="margin-top:500px; margin-bottom:20px;"><hr/></div>')


    # Facultés
    f.write('<h3>Facultés</h3>')
    f.write(
        """
        <div class="grid">
            <div class="col-md-4" 
                style="float:left; padding-right:5px; 
                margin-top:10px; max-height:425px; overflow-y:scroll;">
        """
    )
    f.write(facultes[['Faculté', 'N']].to_html(
        index=False, classes=tableClasses, justify='left')
    )
    
    f.write('</div><div class="col-md-8" style="float:right; padding-right:20px;">')

    f.write(figFacultes.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('</div></div>')
    f.write('<div style="margin-top:500px;"><hr/>')

    # Départements
    f.write('<h3>Départements</h3>')
    f.write(
        """
        <div class="grid">
            <div class="col-md-4" 
                style="float:left; padding-right:5px; 
                margin-top:10px; max-height:425px; overflow-y:scroll;">
        """
    )
    f.write(departements.to_html(
        index=False, classes=tableClasses, justify='left')
    )
    
    f.write('</div><div class="col-md-8" style="float:right; padding-right:20px;">')

    f.write(figDepartements.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('</div></div>')
    f.write('<div style="margin-top:500px;"><hr/>')

    f.write(footer)

### Générer le fichier html pour les unités de recherche
with open('html/expertises.html', 'w', encoding='utf-8') as f:
    f.write(header)
    f.write('<h2>Affiliations</h2></div>')

    # Établissements affiliés
    f.write('<h3>Établissements affiliés</h3>')
    f.write(
        """
        <div class="grid">
            <div class="col-md-4" 
                style="float:left; padding-right:5px; 
                margin-top:10px; max-height:425px; overflow-y:scroll;">
        """
    )

    # Disciplines de recherche
    f.write('<h3>Disciplines</h3>')
    f.write("<p>Principales disciplines de recherche à l'UdeM (Top 30)</p>")
    f.write(figDisciplines.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('<div/">')
    f.write('<div style="margin-top:80px; <hr/>">')
    f.write(figDisciplinesFacultes.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('<div/">')
    f.write(footer)


### Générer le fichier html pour les expertises de recherche


