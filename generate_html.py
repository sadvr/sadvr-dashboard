import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from utils.sadvr_utils import *
from generate_figures import *
from bs4 import BeautifulSoup

tableClasses = ['table', 'table-hover']

with open('./html/header.html', encoding='utf-8') as f:
    header = f.read()

with open('./html/header_index.html') as f:
    header_index = f.read()

with open('./html/footer.html') as f:
    footer = f.read()

### Générer la page d'accueil 
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(header_index)

    ## Ajouter contenu
    f.write("<h2>Vitrine de la recherche UdeM</h2></div>")
    f.write("<p>Bienvenue sur le tableau de bord du SADVR!</p>")
    f.write(
    f""" 
        <div class="grid" 
            style="padding-bottom:30px; width:100%; height:800px; margin-top:40px;">
            <div class="col-md-3" 
                style="float:left; border: 1px solid lightgrey; margin-right:10px; width:22%; border-radius:5px;
                background-color: #F7F7F7; box-shadow: 5px 10px 10px lightgrey;">
                <p style="text-align: center; margin-top:40px; margin-bottom:40px;"><b style="font-size:24px;">{nbProfs}</b><br/>Professeurs</p>
            </div>
            <div class="col-md-3" 
                style="float:left; border: 1px solid lightgrey; margin-left:10px; margin-right:10px; width:22%; border-radius:5px;
                background-color: #F7F7F7; box-shadow: 5px 10px 10px lightgrey;">
                <p style="text-align: center; margin-top:40px; margin-bottom:40px;"><b style="font-size:24px;">{nbDepartements}</b><br/>Départements</p>
            </div>
            <div class="col-md-3" 
                style="float:left; border: 1px solid lightgrey; margin-left:10px; margin-right:10px; width:22%; border-radius:5px;
                background-color: #F7F7F7; box-shadow: 5px 10px 10px lightgrey;">
                <p style="text-align: center; margin-top:40px; margin-bottom:40px;"><b style="font-size:24px;">{nbFacultes}</b><br/>Facultés</p>
            </div>
            <div class="col-md-3"
                style="float:left; border: 1px solid lightgrey; margin-left:10px; width:22%; border-radius:5px;
                background-color: #F7F7F7; box-shadow: 5px 10px 10px lightgrey;">
                <p style="text-align: center; margin-top:40px; margin-bottom:40px;"><b style="font-size:24px;">{nbEtablissementsAffilies}</b><br/>Établissements affiliés</p>
            </div>  

        </div>
    """)

    f.write(footer)

### Générer le fichier html pour les professeurs
with open('html/professeur-e-s.html', 'w', encoding='utf-8') as f:
    f.write(header)
    f.write('<h2>Professeur·e·s - Portrait sociodémographique</h2></div>')
    f.write('<h3>Identité de genre</h3>')
    # Conteneur gauche
    f.write(
        """
        <div class="grid" style="padding-bottom:30px;">
            <div class="col-md-4" 
                style="float:left; padding-right:5px;
                margin-top:10px; max-height:450px; overflow-y:scroll;">
        """
    )
    
    f.write(freqGenreDepartement.to_html(index=False, classes=tableClasses, justify='left'))

    # Conteneur droit
    f.write("""</div>
        <div class="col-md-8" style="float:right; padding-right:35px; padding-left:45px;">
    """)

    f.write('<div style="width:50%">')
    f.write('<select class="form-select" style="margin-bottom:20px;" id="depSelector" onchange="changeDepartment()">')
    for departement in genreDepartement.keys():
        f.write(f'<option value="{genreDepartement[departement]}">{departement}</option>')
        
    f.write('</select></div>')

    f.write("""
        <iframe height="425" width="100%" style="padding:20px;" id="figDepartement" frameborder="0">
        </iframe>
    """)

    f.write(f"""
        <script>
            var figsDepartements = {genreDepartement};
            function changeDepartment() {{
                var selectedDepartment = document.getElementById("depSelector").value;
                document.getElementById("figDepartement").src = selectedDepartment;
            }}

            changeDepartment()
        </script>
    """)

    f.write('</div></div>')

    # Année d'obtention du diplôme - selon le genre
    f.write('<div style="margin-top:475px; width=100%; margin-bottom:20px;"><hr/></div>')
    f.write('<h3>Formation académique</h3>')
    f.write(figAnneDiplomeGenre.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('<div style="margin-top:30px; margin-bottom:20px;"><hr/></div>')

    f.write("<h4>Pays d'obtention du dernier diplôme</h4>")
    f.write(
        """
        <div class="grid" style="margin-top:25px; height:435px;">
        <div class="col-md-4" style="float:left; padding-right:5px; padding-bottom:2px;
        max-height:435px; overflow-y:scroll;">
        """
    )

    # Conteneur gauche
    f.write(paysFormation.to_html(index=False, classes=tableClasses, justify='left'))
    f.write("</div>")
    
    # Conteneur droit
    f.write(
    """
    <div class="col-md-8" style="float:right; width:65%; padding:0px; margin-top:-10px;
    border: 1px solid lightgrey; border-radius:8px;">
    """)
    
    f.write(figPaysFormation.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('</div></div>')
    f.write('<div style="margin-top:50px; margin-bottom:20px;"><hr/></div>')

    # Rang professoral selon le genre
    f.write('<h3>Rang professoral selon le genre</h3>')
    # Conteneur gauche
    f.write(
        """
        <div class="grid" style="margin-top:10px;">
        <div class="col-md-4" style="float:left; padding-right:5px; max-height:450px; overflow-y:scroll;">
        """
    )

    freqFonctionGenre = freqFonctionGenre.rename(
        columns={'genre':'Genre', 'fonction': 'Rang professoral', 'count':'N'}
    )
    f.write(freqFonctionGenre[['Genre', 'Rang professoral', 'N']].to_html(index=False, classes=tableClasses, justify='left'))
    f.write("</div>")

    # Conteneur droit
    f.write("""<div class="col-md-8" style="float:right;
         margin:0px; padding-left:30px; max-height:450px; overflow-y:scroll;">
        """)
    f.write(figFonctionGenre.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('</div></div>')
    f.write('<div style="margin-top:500px; margin-bottom:20px;"><hr/></div>')

    # Langues
    f.write('<h3>Langues</h3>')
    f.write(
        """
        <div class="grid">
            <div class="col-md-6" 
             style="float:left; margin-top: 25px; padding-left:5px; 
             padding-right:5px;"">
        """
    )

    # Conteneur gauche
    f.write(figLanguesParlees.to_html(full_html=False, include_plotlyjs='cdn'))
    
    # Conteneur droit
    f.write("""</div><div class="col-md-6" 
        style="float:right; height:425px; margin:0px;">
        """)
    f.write(figLanguesEcrites.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('</div></div>')

    f.write(footer)


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
        <div class="grid" style="margin-top:10px;">
            <div class="col-md-4" 
                style="float:left; padding-right:5px; 
                height:430px; max-height:430px; overflow-y:scroll;">
        """
    )
    f.write(departements[['Département', 'N']].to_html(
        index=False, classes=tableClasses, justify='left')
    )
    
    f.write("""
        </div><div class="col-md-8" 
        style="float:right; padding-left:30px; max-height:430px; overflow-y:scroll;">
    """)

    f.write(figDepartements.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write('</div></div>')
    f.write('<div style="margin-top:500px;"><hr/>')

    f.write(footer)

### Générer le fichier html pour les expertises de recherche
with open('html/expertises.html', 'w', encoding='utf-8') as f:
    f.write(header)
    f.write('<h2>Expertises de recherche</h2></div>')

    # Disciplines de recherche
    f.write('<h3>Disciplines</h3>')

    # Conteneur gauche
    f.write(
        """
        <div class="grid">
            <div class="col-md-4" 
                style="float:left; 
                margin-top:10px; max-height:450px; overflow-y:scroll;">
        """
    )

    f.write("<p>Nombre de professeur-e-s par discipline</p>")
    table = tableDisciplines[['Discipline', 'N']].to_html(
        index=False, classes=tableClasses, justify='left'
    )
    table = BeautifulSoup(table, 'html.parser')
    table.find('table')['style'] = 'max-heigth:400px; height:300px; overflow-y: scroll;'
    f.write(str(table)
    )

    # Conteneur droit
    f.write('</div><div class="col-md-8" style="float:right;padding-left:45px;">')

    f.write('<div style="width:40%">')
    f.write('<select class="form-select" style="margin-bottom:20px;" id="facultySelector" onchange="changeFaculty()">')
    for faculte in disciplinesFacultes.keys():
        f.write(f'<option value="{disciplinesFacultes[faculte]}">{faculte}</option>')
        
    f.write('</select></div>')

    f.write("""
        <iframe height="425" width="100%" style="padding:20px;" id="figFaculte" frameborder="0">
        </iframe>
    """)

    f.write(f"""
        <script>
            var figsFacultes = {disciplinesFacultes};
            function changeFaculty() {{
                var selectedFaculty = document.getElementById("facultySelector").value;
                document.getElementById("figFaculte").src = selectedFaculty;
            }}

            changeFaculty()
        </script>
    """)

    f.write('</div></div>')
    f.write('<div style="margin-top:500px;"><hr/></div>')

    # Expertises de recherche : mots-clés
    f.write('<h3>Mots-clés</h3>')
    f.write('<p>Principales expertises de recherche par département</p>')

    # Conteneur principal
    f.write('<div style="clear: both;"></div>')
    f.write('<div style="width:40%">')
    f.write('<select class="form-select" style="margin-bottom:20px;" id="fileSelector" onchange="changeIframeSource()">')
    f.write('<option value="../figures/graphs/graph__departement-de-sciences-economiques.html" select>Département de sciences économiques</option><p>&nbps;</p>')

    iFrames = ""
    for graph in graphs[1:]:
        departement = graph['Département']
        fichier = graph['Fichier']
        iFrames += ("\n")
        iFrames += (f'<option value="{fichier}">{departement}</option>')

    iFrames += f"""
        </select></div>
        <div style="clear: both;"></div>
        <!-- Conteneur gauche -->
        <div id="container" class="col-md-6" style="float: left; margin-top:10px; padding-bottom:20px;">
            <iframe id="embeddedFrame" height="600" width="100%" 
                style="margin:-10px; padding:0px; overflow-y:scroll;" frameborder="0">
            </iframe>
        </div>

        <!-- Conteneur droit -->
        <div id="dataTable" class="col-md-6" 
            style="float:right; width:50%; margin-top:10px; max-height:575px; overflow-y:scroll; padding-left:20px; height=600;">
        </div>
        <script>
            var data = {tablesGraphs};
            function changeIframeSource() {{
                var selectedFile = document.getElementById("fileSelector").value;
                document.getElementById("embeddedFrame").src = selectedFile;
            
                var selectedData = data[selectedFile];
                document.getElementById("dataTable").innerHTML = selectedData;
                document.getElementById("dataTable").style.height = "600px"
            }}
        </script>
    """
    f.write(iFrames)
    f.write("""
        <script>changeIframeSource()</script>
            """)
    f.write('<div style="clear: both; margin-top:500px;"><hr/></div>')

    f.write(footer)