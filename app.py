from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pyodbc
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
# Usar una clave secreta fuerte y aleatoria en producción
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'una_clave_secreta_muy_larga_y_aleatoria_para_desarrollo')

# Cadena de conexión a la base de datos desde la variable de entorno
DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")

print(f"DB_CONNECTION_STRING cargada: {DB_CONNECTION_STRING}")

def get_db_connection():
    conn = None
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Error de conexión a la base de datos: {sqlstate}")
        # Opcionalmente, registra el error en un archivo o servicio de monitoreo
    return conn

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", user_name=session.get('user_name'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Users (Name, Email, PasswordHash) VALUES (?, ?, ?)",
                    (name, email, hashed_password)
                )
                conn.commit()
                flash("¡Registro exitoso! Por favor, inicia sesión.", "success")
                return redirect(url_for('login'))
            except pyodbc.IntegrityError:
                flash("Este correo electrónico ya está registrado. Por favor, usa uno diferente.", "danger")
            except Exception as e:
                flash(f"Ocurrió un error durante el registro: {e}", "danger")
            finally:
                conn.close()
        else:
            flash("No se pudo conectar a la base de datos. Por favor, inténtalo de nuevo más tarde.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT UserID, Name, PasswordHash FROM Users WHERE Email = ?", (email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user.PasswordHash, password):
                session['user_id'] = user.UserID
                session['user_name'] = user.Name
                flash("¡Inicio de sesión exitoso!", "success")
                return redirect(url_for('home'))
            else:
                flash("Correo electrónico o contraseña inválidos.", "danger")
        else:
            flash("No se pudo conectar a la base de datos. Por favor, inténtalo de nuevo más tarde.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash("Has cerrado sesión.", "info")
    return redirect(url_for('login'))

@app.route("/calculate_and_save_carbon", methods=["POST"])
def calculate_and_save_carbon():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Usuario no ha iniciado sesión."}), 401

    try:
        factor = float(request.form["transporte"])
        km = float(request.form["kilometros"])
    except ValueError:
        return jsonify({"success": False, "message": "Valores de entrada inválidos."}), 400

    if km < 0:
        return jsonify({"success": False, "message": "Ingresa una distancia válida."}), 400

    huella = factor * km
    recomendacion = ""

    if huella == 0:
        recomendacion = "¡Excelente! No generas emisiones con tu medio de transporte actual."
    elif huella <= 3:
        recomendacion = "Sigue optando por transporte público o compártelo para reducir más tu huella."
    elif huella <= 10:
        recomendacion = "Considera caminar, usar bicicleta o transporte público algunos días de la semana."
    else:
        recomendacion = "Tu huella es alta. Cambiar el uso del automóvil por alternativas sostenibles tendría un gran impacto."

    # Guardar en la base de datos
    user_id = session['user_id']
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO CarbonFootprintCalculations (UserID, WeeklyCO2, Recommendations) VALUES (?, ?, ?)",
                (user_id, huella, recomendacion)
            )
            conn.commit()
            conn.close()
            return jsonify({
                "success": True,
                "huella": f"{huella:.2f}",
                "recomendacion": recomendacion
            })
        except Exception as e:
            conn.close()
            return jsonify({"success": False, "message": f"Error al guardar el cálculo: {e}"}), 500
    else:
        return jsonify({"success": False, "message": "Fallo la conexión a la base de datos."}), 500

if __name__ == "__main__":
    app.run(debug=True)