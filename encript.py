from cryptography.fernet import Fernet

# Paso 2: Generar o cargar una clave
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    try:
        return open("secret.key", "rb").read()
    except FileNotFoundError:
        return generate_key()

# Paso 3: Cifrar el archivo
def encrypt_file(file_name, key):
    f = Fernet(key)
    with open(file_name, "rb") as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(file_name, "wb") as file:
        file.write(encrypted_data)

key = load_key()  # Genera una nueva clave si no existe
encrypt_file("data/data.csv", key)

# Paso 4: Guardar la clave en `.streamlit/secrets.toml` manualmente
print("Guarda esta clave en .streamlit/secrets.toml bajo la clave 'encryption_key':")
print(key.decode())