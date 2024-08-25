import streamlit as st
from cryptography.fernet import Fernet
import pandas as pd
from io import StringIO
from twilio.rest import Client
from geopy.geocoders import Nominatim

# Cargar la clave de cifrado desde .streamlit/secrets.toml
key = st.secrets["KEY"]

# Función para desencriptar el archivo
def decrypt_file(file_name, key):
    f = Fernet(key)
    with open(file_name, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data

# Desencriptar y leer el DataFrame
decrypted_data = decrypt_file('data/data.csv', key)
df = pd.read_csv(StringIO(decrypted_data.decode()), delimiter=';')

# Configurar Twilio
account_sid = st.secrets["SID"]
auth_token = st.secrets["TOKEN"]
client = Client(account_sid, auth_token)

def send_message(body, to):
    message = client.messages.create(
        body=body,
        from_= st.secrets["FROM"],
        to=to
    )
    return message.sid

# Obtener la ubicación del dispositivo
def get_location():
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode("Your Address")
    return f"https://www.google.com/maps?q={location.latitude},{location.longitude}"

# La lógica de la aplicación sigue aquí...
st.title('AVISO EMERGENCIA GRUPO MONTE')

cedula_input = st.text_input('Ingrese el número de cédula', '')

if st.button('SOS'):
    resultado = df[df['Cedula'] == cedula_input]
    if not resultado.empty:
        nombre = resultado.iloc[0]['Nombre']
        sexo = resultado.iloc[0]['Sexo']

        # Enviar primer mensaje con datos personales
        body1 = f"Nombre: {nombre}, Cédula: {cedula_input}, Sexo: {sexo}"
        send_message(body1, st.secrets["TO"])

        # Obtener y enviar la ubicación en un mensaje separado
        ubicacion = get_location()
        body2 = f"Ubicación: {ubicacion}"
        send_message(body2, st.secrets["TO"])

        st.success('Aviso enviado con éxito.')
    else:
        st.error('Cédula no encontrada.')