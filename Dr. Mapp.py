# Dr. Mapp

# Cargamos las librerías necesarias
import streamlit as st
import pandas as pd
import folium
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Igresamos valores iniciales por defecto para que la página no de error
coordenadas = [-27.77392042365015, -64.31305325737927]

# Fefinimos el fondo
page_bg_img = '''
<style>
.stApp {
    background-color: #CEBB9B;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)


# Insertamos el logo y el título
st.image('./dr_voy_logo.jpg')
st.title('¡Podemos ayudarte a encontrar el establecimiento de salud más cercano!')
st.header('Dinos dónde estás y qué distancia puedes recorrer.')


# Cargo los datos del rígido
filepath_HD = 'establecimientos_salud_todos_limpio.csv'
df_final = pd.read_csv(filepath_HD)
df_final.dropna(inplace=True)


# Función para convertir una dirección en coordenadas
def direccion_a_coordenadas(direccion):
    # Inicializar el geocodificador
    geolocator = Nominatim(user_agent="mi_aplicacion_geopy")

    # Obtener la ubicación a partir de la dirección
    ubicacion = geolocator.geocode(direccion)

    # Verificar si se encontró la dirección
    if ubicacion:
        return (ubicacion.latitude, ubicacion.longitude)
    else:
        return None

# Función para calcular la distancia entre dos puntos usando Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers

# Función para encontrar las 10 localizaciones más cercanas
#def encontrar_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset, n, distanciamax):
def encontrar_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset, distanciamax):
    # Crear una lista para almacenar las distancias calculadas
    distancias = []
    cantidad_establecimientos = 0

    # Calcular la distancia para cada localización
    for index, row in dataset.iterrows():
        lat = row['LATITUD']
        lon = row['LONGITUD']
        nombre = row['NOMBRE']
        domicilio = row['DOMICILIO']
        servicio = row['CATEGORIA_TIPOLOGIA']

        # Calcular la distancia desde la referencia
        distancia = calcular_distancia(latitud_referencia, longitud_referencia, lat, lon)

        # Considerar los registros correspondientes a la distancia límite que puede viajar el usuario
        if distancia <= distanciamax:

          # Añadir el nombre de la ubicación y la distancia a la lista
          distancias.append({'nombre': nombre, 'latitud': lat, 'longitud': lon, 'distancia': distancia, 'domicilio': domicilio, 'servicio': servicio})
          cantidad_establecimientos += 1

    # Convertir la lista de distancias a un DataFrame
    distancias_df = pd.DataFrame(distancias)

    # Ordenar el DataFrame por la distancia en orden ascendente
    distancias_df = distancias_df.sort_values(by='distancia')

    # Devolver las 'n' localizaciones más cercanas
    return distancias_df.head(cantidad_establecimientos)

# Función que se ejecuta cuando el usuario hace una selección
# def filtrar_dataframe(change):
    global df_filtrado_global
    if change['type'] == 'change' and change['name'] == 'value':
        # Filtrar el DataFrame según la opción seleccionada
        servicio_seleccionado = change['new']

        # Si se selecciona 'Todos', mostrar todo el DataFrame
        if servicio_seleccionado == 'Todos':
            df_filtrado_global = df_final
        else:
            # Filtrar el DataFrame según el servicio seleccionado
            ##df_filtrado = df[df['País'] == pais_seleccionado]
            df_filtrado_global = df_final[df_final['CATEGORIA_TIPOLOGIA'] == servicio_seleccionado]

        # Limpiar la salida anterior
        #clear_output(wait=True)

        # Mostrar el DataFrame filtrado
        ##print(f"\nFiltrando por servicio: {servicio_seleccionado}")
        ##display(df_filtrado_global.head())

        # Retornar el DataFrame filtrado
        ##return df_filtrado_global

# ------------ NO ESTOY SEGURO SI ESTA PARTE VA -------------------------------

# Función que se ejecuta cuando el botón es presionado
#def mostrar_dataframe(b):
#    #clear_output(wait=True)
#
#   # Mostrar el DataFrame original
#   print("DataFrame original:")
#    display(df_final)

#    # Mostrar el DataFrame filtrado
#    if not df_filtrado_global.empty:
#        print(f"\nFiltrando por servicio: {desplegable.value}")
#        display(df_filtrado_global)
#    else:
#        print("No se ha seleccionado un servicio o el filtro no tiene resultados.")

# ------------------------------------------------------------------------------

# EJECUCIÓN
# Solicitar la dirección al usuario
direccion = st.text_input('Ingrese la dirección (sin acentos, el formato es: dirección, ciudad, país): ')

# Cantidad de establecimientos a mostrar
##cantidad = int(input("Ingrese la cantidad de establecimientos a mostrar: "))

# El usuario tiene que definir una distancia máxima para filtrar los establecimientos
dist_maxima = st.slider('Seleccionar distancia máxima', min_value=0, max_value=50)

# Convertir la dirección en coordenadas
coordenadas = direccion_a_coordenadas(direccion)



latitud_ref = coordenadas[0]
longitud_ref = coordenadas[1]

# # Definir las opciones del desplegable, incluyendo la opción 'Todos'
opciones = ['Todos'] + df_final['CATEGORIA_TIPOLOGIA'].unique().tolist()
opciones = sorted(opciones)

# ---------------- DUDA ----------------
# Acá intento adaptar la selección de tipos de estableciemietos al tipo de widget de streamlit

tipo_elegido = st.multiselect('Elige el tipo de establecimiento que necesitas', opciones)


df_filtrado_global = df_final[df_final['CATEGORIA_TIPOLOGIA'].isin(tipo_elegido)]


# --------------------------------------

# Encontrar las localizaciones más cercanas
##localizaciones_cercanas = encontrar_localizaciones_cercanas(latitud_ref, longitud_ref, df_final, cantidad, dist_maxima)
localizaciones_cercanas = encontrar_localizaciones_cercanas(latitud_ref, longitud_ref, df_filtrado_global, dist_maxima)

# Mostrar las localizaciones cercanas, si existen
if not localizaciones_cercanas.empty:
    st.write(localizaciones_cercanas[['nombre', 'distancia', 'domicilio', 'servicio']])
else:
    st.write("No hay localizaciones dentro del rango especificado.")




# ------------ Creamos el mapa -----------

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
        tipo = row['servicio']

        # Añadir un marcador para cada localización cercana
        folium.Marker(
            [lat, lon],
            popup=f"{nombre} | {tipo} ({distancia:.2f} km)",
            icon=folium.Icon(color='red')
        ).add_to(mapa)
    
    # Creamos una representación en HTML del mapa
    mapa_html = mapa._repr_html_()

    # Devolver el mapa
    return mapa_html


# Generar el mapa con las localizaciones más cercanas
mapa = generar_mapa_localizaciones_cercanas(latitud_ref, longitud_ref, df_filtrado_global)

# Mostrar el mapa
html(mapa, height=700)
