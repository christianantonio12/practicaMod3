import psycopg2
import getpass

# Configuración de conexión a la base de datos en Docker
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "credenciales"
DB_USER = 'Admin'
DB_PASSWORD = "p4sswordDB"

def conectar_db():
    """Conecta a la base de datos PostgreSQL y retorna la conexión."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print("Error de conexión a la base de datos:", e)
        return None

def obtener_datos_usuario(username, password):
    """Consulta la base de datos para obtener los datos de un usuario a partir de sus credenciales."""
    conn = conectar_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        # Verificar si el usuario y contraseña existen en la tabla credenciales
        query = """
            SELECT u.id_usuario, u.nombre, u.correo, u.telefono, u.fecha_nacimiento
            FROM credenciales c
            JOIN usuarios u ON c.id_usuario = u.id_usuario
            WHERE c.username = %s AND c.password_hash = %s;
        """
        cursor.execute(query, (username, password))
        usuario = cursor.fetchone()
        
        if usuario:
            print("\n¡Datos del usuario encontrado!")
            print(f"ID: {usuario[0]}")
            print(f"Nombre: {usuario[1]}")
            print(f"Correo: {usuario[2]}")
            print(f"Teléfono: {usuario[3]}")
            print(f"Fecha de Nacimiento: {usuario[4]}")
        else:
            print("\nUsuario o contraseña incorrectos.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error al consultar la base de datos:", e)

def registrar_usuario():
    """Registra un nuevo usuario y su respectiva credencial en la base de datos."""
    conn = conectar_db()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return

    print("\n--- Registro de Nuevo Usuario ---")
    nombre = input("Nombre completo: ")
    correo = input("Correo electrónico: ")
    telefono = input("Teléfono: ")
    fecha_nacimiento = input("Fecha de nacimiento (AAAA-MM-DD): ")
    
    username = input("Nombre de usuario para el inicio de sesión: ")
    password_hash = getpass.getpass("Contraseña: ")

    try:
        cursor = conn.cursor()

        # 1. Insertar datos en la tabla 'usuarios' y retornar el ID generado
        query_usuario = """
            INSERT INTO usuarios (nombre, correo, telefono, fecha_nacimiento)
            VALUES (%s, %s, %s, %s) RETURNING id_usuario;
        """
        cursor.execute(query_usuario, (nombre, correo, telefono, fecha_nacimiento))
        id_usuario = cursor.fetchone()[0]

        # 2. Insertar credenciales asociadas al nuevo id_usuario
        query_credencial = """
            INSERT INTO credenciales (id_usuario, username, password_hash)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query_credencial, (id_usuario, username, password_hash))

        # Confirmar la transacción en la base de datos
        conn.commit()
        print(f"\n¡Usuario '{username}' registrado exitosamente con ID #{id_usuario}!")

        cursor.close()
        conn.close()

    except Exception as e:
        # Revertir cambios en caso de error (ej. correo o usuario duplicado)
        conn.rollback()
        print("\nError al registrar el usuario:", e)

if __name__ == "__main__":
    while True:
        print("\n==================================")
        print("    SISTEMA DE CREDENCIALES")
        print("==================================")
        print("1. Iniciar sesión")
        print("2. Registrar nuevo usuario")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción (1-3): ")

        if opcion == "1":
            print("\n--- Inicio de Sesión ---")
            user = input("Ingrese su usuario: ")
            pwd = getpass.getpass("Ingrese su contraseña: ")
            obtener_datos_usuario(user, pwd)

        elif opcion == "2":
            registrar_usuario()

        elif opcion == "3":
            print("\n¡Hasta luego!")
            break

        else:
            print("Opción no válida. Intente nuevamente.")