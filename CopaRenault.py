from flask import Flask, render_template, request, jsonify, flash, redirect,session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import firebase_admin
from firebase_admin import credentials, auth
import requests
import pyrebase

firebaseConfig = {
  'apiKey': "AIzaSyBnLNMylTO8bGoO6X-XXdtJ9dTAKOf3LaI",
  'authDomain': "renaultcup-4a1d2.firebaseapp.com",
  'projectId': "renaultcup-4a1d2",
  'storageBucket': "renaultcup-4a1d2.firebasestorage.app",
  'messagingSenderId': "1031158605901",
  'appId': "1:1031158605901:web:2c7f08ec7c34bb33585404",
  'measurementId': "G-67C71NFEQ5",
  'databaseURL':"https://renaultcup-4a1d2-default-rtdb.firebaseio.com/"
}
app = Flask(__name__)
CORS(app,supports_credentials=True)

# Inicializar Firebase
firebase=pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()

# Configuración de Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/RenaultCup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'
app.config['SESSION_COOKIE_SECURE'] = False  # Solo para testing local
app.config['SESSION_COOKIE_SAMESITE'] = "Lax" 
# Inicializar extensiones
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db = SQLAlchemy(app)

# Modelos

class Jugador(db.Model):
    __tablename__ = 'Jugador'
    id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100))
    id_equipo = db.Column(db.Integer)
    DNI = db.Column(db.String(20))
    Telefono = db.Column(db.String(20))
    Email = db.Column(db.String(100))
    Fecha_nacimiento = db.Column(db.String(100))
    Comida_Especial = db.Column(db.String(100))

class Equipo(db.Model):
    __tablename__ = 'Equipo'
    id_equipo = db.Column(db.Integer, primary_key=True)
    Colegio = db.Column(db.String(50))
    Deporte = db.Column(db.String(10))
    Sexo = db.Column(db.String(10))
    Categoria = db.Column(db.String(10))

class Partido(db.Model):
    __tablename__ = 'Partido'
    id_partido = db.Column(db.Integer, primary_key=True)
    Deporte = db.Column(db.String(1))
    Categoria = db.Column(db.String(10))
    Sexo = db.Column(db.String(1))
    Arbitro = db.Column(db.Integer)
    Planillero = db.Column(db.Integer)
    Equipo_1 = db.Column(db.Integer)
    Equipo_2 = db.Column(db.Integer)
    Fase = db.Column(db.String(25))
    Horario_inicio = db.Column(db.String(8))
    Horario_final = db.Column(db.String(8))

class Staff(db.Model):
    __tablename__ = 'Staff'
    id_staff = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(40))
    DNI = db.Column(db.Integer)
    Telefono = db.Column(db.Integer)
    Email = db.Column(db.String(40))
    Trabajo = db.Column(db.String(15))
    Sector = db.Column(db.String(20))

class FirebaseUser(UserMixin):
    def __init__(self, uid, email):
        self.id = uid
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    try:
        user_record = auth.get_user(user_id)
        return FirebaseUser(user_record.uid, user_record.email)
    except:
        return None

def firebase_login(email, password):
    api_key = firebaseConfig["apiKey"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()
    return None

@app.route("/signup", methods=["POST"])
def signupApi():
    try:
        data = request.get_json()
        nombre = data.get("Nombre")
        email = data.get("Email")
        password = data.get("Contraseña")

        if not (nombre and email and password):
            return jsonify({"success": False, "error": "Faltan campos"}), 400

        user_record = auth.create_user_with_email_and_password(email, password)

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@app.route("/login", methods=["POST"])
def loginApi_Post():
    try:
        data = request.get_json()
        email = data.get("Email")
        password = data.get("Contraseña")

        if not (email and password):
            return jsonify({"success": False, "error": "Faltan datos"}), 400

        user_info = firebase_login(email, password)
        if user_info is None:
            return jsonify({"success": False, "error": "Credenciales incorrectas"}), 401

        uid = user_info.get("localId")
        user = FirebaseUser(uid=uid, email=email)
        login_user(user)
        flash(current_user.email)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/loginGET", methods=["GET"])
def loginApi_Get():
    print(current_user.email)
    try:
        if current_user.is_authenticated:
            result = [{
                'email': current_user.email
            }]
            return jsonify({'success': True, 'user': result})
        else:
            return jsonify({'success': False, 'error': 'Usuario no autenticado'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/login")
def login():
    return render_template('login.html')
@app.route("/logout")
@login_required
def logout():
    current_user.is_authenticated
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
def Index():
    return render_template('Index.html')

@app.route("/Add Player")
def Create_Player():
    return render_template('Add_Player.html')

@app.route("/Add Equipo")
def hell():
    return render_template('Add_Equipo.html')

@app.route("/Add Match")
def Create_Match():
    return render_template('Add_Match.html')

@app.route("/Add Staff")
def Create_Staff():
    return render_template('Add_Staff.html')

@app.route('/api/Staff', methods=['POST'])
def add_Staff():
    try:
        data = request.get_json()
        Nombre = data.get('Nombre')
        DNI = data.get('DNI')
        Telefono = data.get('Telefono')
        Email = data.get('Email')
        Trabajo = data.get('Trabajo')
        Sector = data.get('Sector')

        if not (Nombre and DNI and Telefono and Email and Trabajo and Sector):
            return jsonify({'success': False, 'error': 'Faltan campos requeridos'}), 400

        new_staff = Staff(
            Nombre=Nombre,
            DNI=DNI,
            Telefono=Telefono,
            Email=Email,
            Trabajo=Trabajo,
            Sector=Sector
        )

        db.session.add(new_staff)
        db.session.commit()

        return jsonify({
            'success': True,
            'Staff': {
                'id_staff': new_staff.id_staff,
                'Nombre': new_staff.Nombre,
                'DNI': new_staff.DNI,
                'Telefono': new_staff.Telefono,
                'Email': new_staff.Email,
                'Trabajo': new_staff.Trabajo,
                'Sector': new_staff.Sector
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/Equipo', methods=['POST'])
def add_Equipo():
    try:
        data = request.get_json()
        Colegio = data.get('Colegio')
        Deporte = data.get('Deporte')
        Sexo = data.get('Sexo')
        Categoria = data.get('Categoria')


        if not (Colegio and Deporte and Sexo and Categoria):
            return jsonify({'success': False, 'error': (Colegio , Deporte , Sexo , Categoria)}), 400

        new_Equipo = Equipo(
            Colegio=Colegio,
            Deporte=Deporte,
            Sexo=Sexo,
            Categoria=Categoria
        )

        db.session.add(new_Equipo)
        db.session.commit()
  
        return jsonify({
            'success': True,
            'Equipo': {
                'id_equipo': Equipo.id_equipo,
                'Colegio':Equipo.Colegio,
                'Deporte':Equipo.Deporte,
                'Sexo':Equipo.Sexo,
                'Categoria':Equipo.Categoria
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/Equipo', methods=['GET'])
def get_Equipos():
    try:
        new_Equipo = Equipo.query.all()
        result = []
        for j in new_Equipo:
            result.append({
                'id_equipo': Equipo.id_equipo,
                'Colegio':Equipo.Colegio,
                'Deporte':Equipo.Deporte,
                'Sexo':Equipo.Sexo,
                'Categoria':Equipo.Categoria
            })
        return jsonify({'success': True, 'Equipo': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/Players', methods=['POST'])
def add_Player():
    try:
        data = request.get_json()
        Nombre = data.get('Nombre')
        Fecha_nacimiento = data.get('Fecha_nacimiento')
        DNI = data.get('DNI')
        id_equipo = data.get('id_equipo')
        Telefono = data.get('Telefono')
        Email = data.get('Email')
        Comida_especial = data.get('Comida_especial')

        if not (Nombre and Fecha_nacimiento and DNI and id_equipo and Telefono and Email and Comida_especial):
            return jsonify({'success': False, 'error': (Nombre , Fecha_nacimiento , DNI , id_equipo , Telefono , Email , Comida_especial)}), 400

        new_Jugador = Jugador(
            Nombre=Nombre,
            Fecha_nacimiento=Fecha_nacimiento,
            DNI=DNI,
            id_equipo=id_equipo,
            Telefono=Telefono,
            Email=Email,
            Comida_Especial=Comida_especial
        )

        db.session.add(new_Jugador)
        db.session.commit()

        return jsonify({
            'success': True,
            'Jugador': {
                'id': Jugador.id,
                'Nombre': Jugador.Nombre,
                'id_equipo': Jugador.id_equipo,
                'DNI': Jugador.DNI,
                'Telefono': Jugador.Telefono,
                'Email': Jugador.Email,
                'Fecha_nacimiento': Jugador.Fecha_nacimiento,
                'Comida_Especial': Jugador.Comida_Especial
                
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/Players', methods=['GET'])
def get_Jugadores():
    try:
        nuevo_Jugador = Jugador.query.all()
        result = []
        for j in nuevo_Jugador:
            result.append({
                'id': j.id,
                'Nombre': j.Nombre,
                'Fecha_nacimiento': j.Fecha_nacimiento,
                'DNI': j.DNI,
                'id_equipo': j.id_equipo,
                'Telefono': j.Telefono,
                'Email': j.Email,
                'Comida_Especial': j.Comida_Especial
            })
        return jsonify({'success': True, 'Jugador': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/api/Matches', methods=['POST'])
def add_Matches():
    try:
        data = request.get_json()
        Deporte = data.get('Deporte')
        Categoria = data.get('Categoria')
        Sexo = data.get('Sexo')
        Equipo_1 = data.get('Equipo_1')
        Equipo_2 = data.get('Equipo_2')
        Arbitro = data.get('Arbitro')
        Planillero = data.get('Planillero')
        Horario_inicio = data.get('Horario_inicio')
        Horario_final = data.get('Horario_final')

        if not (Deporte and Sexo and Equipo_1 and Equipo_2 and Arbitro and Planillero and Horario_inicio and Horario_final):
            return jsonify({'success': False, 'error': (Deporte , Categoria , Sexo , Equipo_1 , Equipo_2 , Arbitro , Planillero , Horario_inicio , Horario_final)}), 400
        
        new_Partido = Partido(
            Deporte=Deporte,
            Categoria=Categoria,
            Sexo=Sexo,
            Equipo_1=Equipo_1,
            Equipo_2=Equipo_2,
            Arbitro=Arbitro,
            Planillero=Planillero,
            Horario_inicio=Horario_inicio,
            Horario_final=Horario_final
        )

        db.session.add(new_Partido)
        db.session.commit()

        return jsonify({
            'success': True,
            'Partido': {
                'Deporte': Partido.Deporte,
                'Categoria': Partido.Categoria,
                'Sexo': Partido.Sexo,
                'Equipo_1': Partido.Equipo_1,
                'Equipo_2': Partido.Equipo_2,
                'Arbitro': Partido.Arbitro,
                'Planillero': Partido.Planillero,
                'Horario_inicio': Partido.Horario_inicio,
                'Horario_final': Partido.Horario_final
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/Matches', methods=['GET'])
def get_Matches():
    try:
        new_Match = Partido.query.all()
        result = []
        for j in new_Match:
            result.append({
                'id_partido': Partido.id_partido,
                'Deporte': Partido.Deporte,
                'Categoria': Partido.Categoria,
                'Sexo': Partido.Sexo,
                'Equipo_1': Partido.Equipo_1,
                'Equipo_2': Partido.Equipo_2,
                'Arbitro': Partido.Arbitro,
                'Planillero': Partido.Planillero,
                'Horario_inicio': Partido.Horario_inicio,
                'Horario_final': Partido.Horario_final
            })
        return jsonify({'success': True, 'Equipo': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    

