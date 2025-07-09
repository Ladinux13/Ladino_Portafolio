#%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%
##%%%%%%%%%%%%%%%%#%%
# TABLERO PARA LAS SUPERVICIONES
##%%%%%%%%%%%%%%%%#%%
#### Ladino Álvarez Ricardo Arturo
##%%%%%%%%%%%%%%%%#%%


#%%%%%%%%%%%%%%%% Librerias base %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

import os
import hmac
import numpy as np
import pandas as pd
from io import BytesIO
import streamlit as st
import geopandas as gpd

#%%%%%%%%%%%%%%%% Funciones de los gráficos %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

from GRAFICAS_DASHBOARD import MAPA_MENU, DONA_MENU, BARRAS_MENU
from GRAFICAS_DASHBOARD import CONFIABILIDAD, QUEJA_DENUNCIA, RIESGO_ATENCION_NIVEL

#%%%%%%%%%%%%%%%% Funciones de los contenedores %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# 

from CONTENEDORES_DASHBOARD import Contenedor_Titulo, Contenedor_Hacienda, Contenedor_SAT
from CONTENEDORES_DASHBOARD import CONTENEDOR_M, CONTENEDOR_PR, CONTENEDOR_QDNA

##%%%%%%%%%%%%%%%%#%%
##%%%%%%%%%%%%%%%%#%%

#> Titulo de la pagina
st.set_page_config(page_title = 'Análisis del Riesgo', 
                   layout = 'wide',
                   page_icon = r"C:/Users/LAAR8976/Ladino_ALL/CECTI/DASHBOARD_RIESGOS_CECTI/TABLERO/.image/Logo.jpg")


#> Leer el contenido del archivo CSS
with open(bootstrap_css_path, "r") as f:
    bootstrap_css_content = f.read()


#%%%%%%%%%%%%%%%% Barra lateral - Filtro UAD %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#>
st.sidebar.header("UNIDADES ADMINISTRATIVAS")

#> Crear la lista de unidades administrativas únicas a partir de ambas tablas
UAD_1_RIESGO = BASE_RIESGO["UNIDAD"].unique().tolist()
UAD_1_DENUNCIAS = BASE_DENUNCIAS["UNIDAD"].unique().tolist()

#> Unir las listas de unidades y eliminar duplicados
UAD_1 = sorted(list(set(UAD_1_RIESGO + UAD_1_DENUNCIAS)))

#> Crear el selector en la barra lateral
UAD_DROP = st.sidebar.multiselect("Seleccionar por Unidad:",
                                   options=UAD_1,
                                   default=[],  # Ninguna seleccionada por defecto
                                   key='UAD_DROP'
                                   )

#> Inicializar las variables para que estén accesibles fuera del bloque
BASE_RIESGOS_UNIDAD = pd.DataFrame()
BASE_DENUNCIAS_UNIDAD = pd.DataFrame()

#> Verificar si se seleccionaron unidades
if not UAD_DROP:
    st.sidebar.warning("⚠️ No se han seleccionado datos")
else:
    #> Filtrar los DataFrames
    BASE_RIESGOS_UNIDAD = BASE_RIESGO[BASE_RIESGO["UNIDAD"].isin(UAD_DROP)]
    BASE_DENUNCIAS_UNIDAD = BASE_DENUNCIAS[BASE_DENUNCIAS["UNIDAD"].isin(UAD_DROP)]


####################################################


## Crear pestañas
General_T, Riesgo_T, Aplica_T, Denuncia_T = st.tabs(["INFORMACIÓN GENERAL", "RIESGO POR PUESTOS", "RIESGO POR APLICATIVOS", "DENUNCIAS"])


with General_T:
    st.success('INFORMACIÓN GENERAL')
    if BASE_RIESGOS_UNIDAD.empty:
        st.warning("No hay datos disponibles para la selección actual.")

    else:

        Menu_conte = CONTENEDOR_M(BASE_RIESGOS_UNIDAD)
        st.markdown(Menu_conte, unsafe_allow_html=True) 

        MENU_1, MENU_2 = st.columns([2, 2])

        with MENU_1:
            MAPA_UAD = MAPA_MENU (BASE_RIESGOS_UNIDAD, BASE_MAPA)
            st.plotly_chart(MAPA_UAD, use_container_width = True)

        with MENU_2:
            PUESTOS_UAD = DONA_MENU(BASE_RIESGOS_UNIDAD,'PTO_RIESGO')
            st.plotly_chart(PUESTOS_UAD, use_container_width = True)

        PUESTOS_RIESGO = BARRAS_MENU(BASE_RIESGOS_UNIDAD)
        st.plotly_chart(PUESTOS_RIESGO, use_container_width = True)
  


with Riesgo_T:
    st.success('RIESGO POR ADMINISTRACIÓN')

    if BASE_RIESGOS_UNIDAD.empty:
        st.warning("No hay datos disponibles para la selección actual.")

    else:
        DESCO_DROP_2 = BASE_RIESGOS_UNIDAD["DESCONCENTRADA"].dropna().unique().tolist() + ['TODAS']
        DESCO_DROP = st.multiselect('Seleccionar por ADMINISTRACIÓN', 
                                     DESCO_DROP_2, 
                                     default = 'TODAS', 
                                     key = 'DESCO_DROP')
        if 'TODAS' in DESCO_DROP:
            DESCO_DROP = DESCO_DROP_2[:-1]
            

        BASE_RIESGOS_DESCO = BASE_RIESGOS_UNIDAD.query("DESCONCENTRADA == @DESCO_DROP")

        if BASE_RIESGOS_DESCO.empty:
            st.warning("NO HAY DATOS DISPONIBLES PARA LA SELECCIÓN ACTUAL.")

        else: 
            PUESTOS_T,PUESTOS_R = Puestos_Metricas(BASE_RIESGOS_DESCO)
            
            METRIC_PT, METRIC_PR = st.columns(2)
            with METRIC_PT:
                st.metric('Total de puestos', PUESTOS_T)
            with METRIC_PR:
                st.metric('Puestos de riesgo', PUESTOS_R)

            PTO_ADM_1, PTO_ADM_2 = st.columns([2,1])
            with PTO_ADM_1:
                PUESTOS_RIESGO_DESCO = BARRAS_MENU(BASE_RIESGOS_DESCO)
                st.plotly_chart(PUESTOS_RIESGO_DESCO, use_container_width = True)
            with PTO_ADM_2:
                Puesto_riesgo_conte = CONTENEDOR_PR(BASE_RIESGOS_DESCO)
                st.markdown(Puesto_riesgo_conte, unsafe_allow_html=True) 

            st.success('CONFIABILIDAD, QUEJAS & DENUNCIAS Y NIVEL DE RIESGO')
            
              


with Aplica_T:
    st.success('RIESGO POR APLICATIVOS')

    if BASE_RIESGOS_UNIDAD.empty:
        st.warning("No hay datos disponibles para la selección actual")

    else:

        APP_TOT = APLICATIVOS_TOTAL(BASE_RIESGOS_UNIDAD)
        st.plotly_chart(APP_TOT, use_container_width=True)


        CONTE_APP_R = APLICATIVOS_RIESGOS(BASE_RIESGOS_UNIDAD)
        st.markdown(CONTE_APP_R, unsafe_allow_html=True) 


        APP_PTO = APLICATIVOS_PUESTOS (BASE_RIESGOS_UNIDAD)
        st.plotly_chart(APP_PTO, use_container_width=True)

        DESCO_APP_2 = BASE_RIESGOS_UNIDAD["DESCONCENTRADA"].dropna().unique().tolist() + ['TODAS']
        DESCO_APP = st.multiselect('Seleccionar por ADMINISTRACIÓN', 
                                     DESCO_APP_2, 
                                     default = 'TODAS', 
                                     key = 'DESCO_APP')
        if 'TODAS' in DESCO_APP:
            DESCO_APP = DESCO_APP_2[:-1]
            

        BASE_RIESGOS_APP = BASE_RIESGOS_UNIDAD.query("DESCONCENTRADA == @DESCO_APP")



with Denuncia_T:
    st.success('DETALLE DE LAS DENUNCIAS')

    if BASE_DENUNCIAS_UNIDAD.empty:
        st.warning("No hay datos disponibles para la selección actual")
    else:

        CONTE_DENUN = DENUNCIAS_CONTE(BASE_DENUNCIAS_UNIDAD)
        st.markdown(CONTE_DENUN, unsafe_allow_html=True) 

        ASUNTOS, DENUNCIA_QUEJA, PUESTOS = DENUNCIAS_INFO(BASE_DENUNCIAS_UNIDAD)

        VELO_INFO = VEL_DENU(DENUNCIA_QUEJA)
        st.plotly_chart(VELO_INFO, use_container_width=True)

        
hide_streamlit_style = """
                      <style>
                      #MainMenu {visibility: hidden;}
                      footer {visibility: hidden;}
                      </style>
                      """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)