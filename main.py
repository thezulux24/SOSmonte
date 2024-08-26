from flask import Flask, request, render_template_string, jsonify, send_from_directory, redirect, url_for
from cryptography.fernet import Fernet
import pandas as pd
from io import StringIO
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Claves y tokens
key = os.getenv('KEY')
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
from_ = os.getenv('FROM')
to = os.getenv('TO')

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
client = Client(account_sid, auth_token)

def send_message(body, to):
    message = client.messages.create(
        body=body,
        from_=from_,
        to=to
    )
    return message.sid

@app.route('/logo.png')
def logo():
    return send_from_directory('src', 'logo.png')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cedula_input = request.form['cedula']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        resultado = df[df['Cedula'] == cedula_input]
        if not resultado.empty:
            nombre = resultado.iloc[0]['Nombre']
            sexo = resultado.iloc[0]['Sexo']

            # Enviar primer mensaje con datos personales
            body1 = f"Nombre: {nombre}, Cédula: {cedula_input}, Sexo: {sexo}"
            send_message(body1, to)

            # Enviar la ubicación en un mensaje separado
            ubicacion = f"https://www.google.com/maps?q={latitude},{longitude}"
            body2 = f"Ubicación: {ubicacion}"
            send_message(body2, to)

            return redirect(url_for('success'))
        else:
            return "Cédula no encontrada."
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <title>SOS App</title>
        </head>
        <body class="bg-light">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card mt-5">
                            <div class="card-body">
                                <h5 class="card-title text-center">Situación Emergencia Carrera</h5>
                                <div class="text-center">
                                    <img src="/logo.png" alt="Logo" class="img-fluid" style="width: 100px;">
                                </div>
                                <p>1. Mantente en el lugar desde el cual envías la señal de ayuda.</p>
                                <p>2. Por favor concede el permiso de UBICACIÓN GPS a la web, de esta manera podremos saber dónde estás para ir por ti.</p>
                                <form method="post" onsubmit="getLocation(event)">
                                    <div class="form-group">
                                        <label for="cedula">Ingrese el número de cédula:</label>
                                        <input type="text" class="form-control" id="cedula" name="cedula" required>
                                    </div>
                                    <input type="hidden" id="latitude" name="latitude">
                                    <input type="hidden" id="longitude" name="longitude">
                                    <button type="submit" class="btn btn-primary btn-block">SOS</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            <script>
                function getLocation(event) {
                    event.preventDefault();
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(function(position) {
                            document.getElementById('latitude').value = position.coords.latitude;
                            document.getElementById('longitude').value = position.coords.longitude;
                            event.target.submit();
                        });
                    } else {
                        alert("Geolocation is not supported by this browser.");
                    }
                }
            </script>
        </body>
        </html>
    ''')

@app.route('/success')
def success():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <title>SOS Enviado</title>
        </head>
        <body class="bg-light">
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card mt-5">
                            <div class="card-body text-center">
                                <h5 class="card-title">¡Aviso enviado con éxito!</h5>
                                <p class="card-text">Tu señal de ayuda ha sido enviada. Mantente en el lugar y espera asistencia.</p>
                                <a href="/" class="btn btn-primary">Volver</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        </body>
        </html>
    ''')
