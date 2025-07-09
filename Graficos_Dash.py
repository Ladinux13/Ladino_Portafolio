#%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%
#
# TABLERO PARA LAS SUPERVICIONES - GRAFICOS
#
#> Autor: Ladino Álvarez Ricardo Arturo



#%%%%%%%%%%%%%%%% Librerias de uso base %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.colors as mcolors

#%%%%%%%%%%%%%%%% Graficos del menu %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#> Gráfica de Mapa-Menu
def MAPA_MENU(Tabla, GeoJson):
    """Genera un mapa interactivo basado en una tabla y un GeoJSON."""
    UNIDADES = Tabla.iloc[:, 0].unique()
    GeoJson['color'] = GeoJson['UNIDAD_ADM'].apply(lambda x: 'red' if x in UNIDADES else 'grey')
   
    # Filtrar geometrías de las regiones seleccionadas
    geometries = GeoJson[GeoJson['UNIDAD_ADM'].isin(UNIDADES)]['geometry']

    # Calcular los límites combinados de las regiones seleccionadas
    if not geometries.empty:
        combined_bounds = geometries.total_bounds  # [minx, miny, maxx, maxy]
        center_lat = (combined_bounds[1] + combined_bounds[3]) / 2
        center_lon = (combined_bounds[0] + combined_bounds[2]) / 2

        # Ajustar el nivel de zoom basado en la extensión
        zoom = 8  # Valor por defecto
        extent_lat = combined_bounds[3] - combined_bounds[1]
        extent_lon = combined_bounds[2] - combined_bounds[0]
        max_extent = max(extent_lat, extent_lon)
        if max_extent > 0:
            zoom = max(3, min(10, 12 - max_extent))  # Zoom dinámico según la extensión
    else:
        # Si no hay regiones seleccionadas, usar valores predeterminados
        center_lat, center_lon, zoom = 23.798375, -102.5821213, 3.5 

    return (MAPA)

#%%%%%%
#>  Gráfica de Dona-Menu

def DONA_MENU(Tabla, Variable):
    """Genera una gráfica de dona para mostrar puestos con y sin riesgo."""
    Labels = ['Puesto con Riesgo', 'Puesto sin Riesgo']
    Total = Tabla.PUESTO_NOM.nunique()
    Values = [Tabla[Tabla[Variable] == 'SI'].PUESTO_NOM.nunique(),
              Tabla[Tabla[Variable] == 'NO'].PUESTO_NOM.nunique()
             ]

    PASTEL = go.Figure(data = [go.Pie(labels = Labels,
                                      values = Values,
                                      hole = 0.5,
                                      textinfo = 'label+value+percent',
                                      hoverinfo = 'label+value+percent',
                                      texttemplate = '%{label}<br>%{value} (%{percent})',
                                      textposition = 'outside',
                                      marker=dict(colors = ['rgb(99,13,50)', 'rgb(111, 111, 113)'],
                                                  line = dict(color = '#FFFFFF', width = 0.5)
                                                  )
                                      )
                               ]
                      )
    return (PASTEL)



#%%%%%%
#>  Gráfica de Barras-Menu & Riesgos
def BARRAS_MENU(Tabla):
    """Genera una gráfica de barras para mostrar la distribución de empleados por puesto."""
    VSN = (Tabla[Tabla['PTO_RIESGO'] == 'SI']
           .groupby(['CVE_UNIDAD', 'UNIDAD', 'PUESTO_NOM'])['EMPLEADO']
           .nunique()
           .reset_index()
           .sort_values(by = ['EMPLEADO'], ascending = False))
    
    VSN['PUESTO_NOM_ORD'] = VSN['PUESTO_NOM'].astype(str) + ' '
    
    unique_positions = VSN['PUESTO_NOM_ORD'].unique()
    num_positions = len(unique_positions)
    
    cmap = mcolors.LinearSegmentedColormap.from_list("", ['#630d32', '#b18f5f', '#6f6f71'])
    colors = ([mcolors.to_hex(cmap(i / (num_positions - 1))) for i in range(num_positions)]
              if num_positions > 1 else [mcolors.to_hex(cmap(0))])
    
    color_map = dict(zip(unique_positions, colors))
    
    BARRAS = px.bar(VSN,
                    y = 'EMPLEADO',
                    x = 'PUESTO_NOM_ORD',
                    orientation = 'v',
                    color = 'PUESTO_NOM_ORD',
                    color_discrete_map = color_map,
                    text = 'EMPLEADO'
                    )
    
    # Configuración general de la gráfica
    BARRAS.update_traces(marker_line_width = 0.5,
                         textposition = 'auto',
                         hovertemplate = None,
                         hoverinfo = 'none'
                         )
    
    return (BARRAS)



#%%%%%%
#>  Gráfica de Nivel Atención-Riesgos
def RIESGO_ATENCION_NIVEL(Tabla):
    """Genera una gráfica de Treemap alineando colores con el nivel de atención."""
    # Agrupación de datos
    nivel_riesgo = (Tabla.groupby('NIVEL_ATENCION')['EMPLEADO'].nunique().reset_index().sort_values(by =['EMPLEADO'], 
                                                                                                    ascending = False))

    # Diccionario de colores alineados con NIVEL_ATENCION
    nivel_colores = {'NULO': '#6f6f71',
                     'BAJO': '#907f68',
                     'MEDIO': '#b18f5f',
                     'ALTO': '#8a4e48',
                     'CRITICO': '#630d32'
                     }

    # Mapear colores a las clases de NIVEL_ATENCION
    colors = nivel_riesgo['NIVEL_ATENCION'].map(nivel_colores)

    # Creación de la gráfica de Treemap
    tree_atencion = go.Figure(go.Treemap(labels = nivel_riesgo['NIVEL_ATENCION'],
                                         parents = [""] * len(nivel_riesgo['NIVEL_ATENCION']),
                                         values = nivel_riesgo['EMPLEADO'],
                                         marker = dict(colors = colors),
                                         textinfo = 'label+value',
                                         textposition = 'middle center'
                                         )
                              )

    # Configuración de diseño
    tree_atencion.update_layout(title = "",
                                font = dict(
                                family = "Geomanist Light",
                                size = 12,
                                color = '#000000'),
                                template = None,
                                showlegend = False,
                                margin = {"r": 0, "t": 0, "l": 0, "b": 0},
                                uniformtext = dict(minsize = 14, mode = 'hide')
                                )

    # Configuración de trazos
    tree_atencion.update_traces(hovertemplate = None, hoverinfo = 'none')

    return (tree_atencion)


#%%%%%%
#>  Gráfica de Aplicativos & Puestos - Aplicativos
def APLICATIVOS_PUESTOS (Tabla):
    ''' '''
    TOT_APP = Tabla.groupby('PUESTO_NOM')['APLICATIVO'].nunique().reset_index().sort_values(by=['APLICATIVO'], 
                                                                                            ascending=False)
    cmap = mcolors.LinearSegmentedColormap.from_list("", ['#630d32', '#b18f5f', '#6f6f71'])
    num_apps = len(TOT_APP)
    colors = [mcolors.to_hex(cmap(i / (num_apps - 1))) for i in range(num_apps)]
    max_value = TOT_APP['APLICATIVO'].max()
    pull_values = [0.05 if val > 0.9 * max_value else 0 for val in TOT_APP['APLICATIVO']]

    PASTEL_APP = px.pie(TOT_APP,
                        names = 'PUESTO_NOM',
                        values = 'APLICATIVO')
    
    return (PASTEL_APP)



#%%%%%%
#>  Tipo de clase - Denuncias
def VEL_DENU(Tabla):
    """Genera velocímetros distribuidos dinámicamente en filas y columnas."""
    Veloc = go.Figure()

    # Número de columnas por fila
    cols = 3
    num_elements = len(Tabla)  # Número de elementos
    rows = (num_elements + cols - 1) // cols  # Calcular el número de filas necesarias

    # Crear los velocímetros
    for i, row in Tabla.iterrows():
        # Calcular el valor máximo dinámico basado en la suma de todas las clases del velocímetro
        max_value = Tabla[Tabla['D15'] == row['D15']]['VALUE'].sum() * 1.1

        Veloc.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=row['VALUE'],
                title={"text": row['D15'], "font": {"size": 13}},  # Reducir el tamaño de la letra aquí
                gauge={
                    'axis': {'range': [0, max_value]},
                    'bar': {'color': "#630d32"},
                    'steps': [{'range': [0, max_value], 'color': "#F1F1E8"}],
                    'threshold': {
                        'line': {'color': "#000000", 'width': 4},
                        'thickness': 0.75,
                        'value': max_value * 0.9
                    }
                },
                domain={'row': i // cols, 'column': i % cols}
            )
        )

    return (Veloc)


#%%%%%%
#>  Puestos con más folios - Denuncias
def DENUNCIAS_PUESTOS(Tabla):
    ''' '''
    Tabla['D8_O'] = Tabla['D8'].astype(str) + ' '
    unique_positions = Tabla['D8_O'].unique()
    num_positions = len(unique_positions)

    cmap = mcolors.LinearSegmentedColormap.from_list("", ['#630d32','#b18f5f', '#6f6f71'])

    if num_positions > 1:
        colors = [mcolors.to_hex(cmap(i/(num_positions -1))) for i in range(num_positions)]
    else:
        colors = [mcolors.to_hex(cmap(0))]

    color_map = dict(zip(unique_positions, colors))
    
    BARRAS = px.bar(Tabla,
                    y = 'VALUE',
                    x = 'D8_O',
                    orientation = 'v',
                    color = 'D8_O',
                    color_discrete_map = color_map,
                    text = 'VALUE'
                    )

    return (BARRAS)


#%%%%%%
#>  Gráfica de Aplicativos & Puestos - Denuncias
def CLASES_DENUNCIAS (Tabla):
    ''' '''
    cmap = mcolors.LinearSegmentedColormap.from_list("", ['#630d32', '#b18f5f', '#6f6f71'])
    num_apps = len(Tabla)
    colors = [mcolors.to_hex(cmap(i / (num_apps - 1))) for i in range(num_apps)]
    max_value = Tabla['VALUE'].max()
    pull_values = [0.05 if val > 0.9 * max_value else 0 for val in Tabla['VALUE']]

    PASTEL_APP = px.pie(Tabla,
                        names = 'D14',
                        values = 'VALUE')
    
    PASTEL_APP.update_traces(pull = pull_values,
                             marker = dict(colors = colors,
                                           line = dict(color = '#FFFFFF',
                                                       width = 0.5)),
                             textposition ='auto',
                             textinfo ='label+percent', 
                             insidetextorientation = 'radial',
                             hovertemplate = None, 
                             hoverinfo= 'none'
                            )
    return (PASTEL_APP)

