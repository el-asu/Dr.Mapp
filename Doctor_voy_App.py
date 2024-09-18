#Doctor Voy - App

# Cargamos las librerías necesarias
import streamlit as st
import pandas as pd
import folium
from geopy.distance import geodesic

st.title('Doctor Voy')
st.header('¡Podemos ayudarte a encontrar el establecimiento de salud más cercano! \nSólo debes conocer tu latitud y longitud.')


# Cargo los datos del rígido
filepath_HD = 'nomb_geoloc_limpios.csv'
df = pd.read_csv(filepath_HD)
df.dropna(inplace=True)



# Función para calcular la distancia entre dos puntos usando Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers



# Función para encontrar las 10 localizaciones más cercanas
def encontrar_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset, n=10):
    # Crear una lista para almacenar las distancias calculadas
    distancias = []

    # Calcular la distancia para cada localización
    for index, row in dataset.iterrows():
        lat = row['LATITUD']
        lon = row['LONGITUD']
        nombre = row['NOMBRE']

        # Calcular la distancia desde la referencia
        distancia = calcular_distancia(latitud_referencia, longitud_referencia, lat, lon)

        # Añadir el nombre de la ubicación y la distancia a la lista
        distancias.append({'nombre': nombre, 'latitud': lat, 'longitud': lon, 'distancia': distancia})

    # Convertir la lista de distancias a un DataFrame
    distancias_df = pd.DataFrame(distancias)

    # Ordenar el DataFrame por la distancia en orden ascendente
    distancias_df = distancias_df.sort_values(by='distancia')

    # Devolver las 'n' localizaciones más cercanas
    return distancias_df.head(n)



# Pedir latitud y longitud como parámetros
latitud_ref = st.number_input('Ingresar la latitud')
longitud_ref = st.number_input('Ingresar la longitud')
#-31.419706716326104, -64.18829654750853

# Encontrar las 10 localizaciones más cercanas
localizaciones_cercanas = encontrar_localizaciones_cercanas(latitud_ref, longitud_ref, df)

# Mostrar las 10 localizaciones más cercanas
st.write(localizaciones_cercanas)


from streamlit.components.v1 import html

# Función para generar el mapa con las localizaciones más cercanas
def generar_mapa_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset):
    # Encontrar las 5 localizaciones más cercanas
    ##localizaciones_cercanas = encontrar_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset)

    # Crear el mapa centrado en la localización de referencia
    mapa = folium.Map(location=[latitud_ref, longitud_ref], zoom_start=7)

    # Añadir un marcador para la localización de referencia
    folium.Marker(
        [latitud_ref, longitud_ref],
        popup="Punto de referencia",
        icon=folium.Icon(color='blue')
    ).add_to(mapa)

    # Añadir marcadores para las 10 localizaciones más cercanas
    for index, row in localizaciones_cercanas.iterrows():
        lat = row['latitud']
        lon = row['longitud']
        nombre = row['nombre']
        distancia = row['distancia']

        # Añadir un marcador para cada localización cercana
        folium.Marker(
            [lat, lon],
            popup=f"{nombre} ({distancia:.2f} km)",
            icon=folium.Icon(color='red')
        ).add_to(mapa)
    
    # Creamos una representación en HTML del mapa
    mapa_html = mapa._repr_html_()

    # Devolver el mapa
    return mapa_html


# Generar el mapa con las localizaciones más cercanas
mapa = generar_mapa_localizaciones_cercanas(latitud_ref, longitud_ref, df)

# Mostrar el mapa
html(mapa, height=500)
