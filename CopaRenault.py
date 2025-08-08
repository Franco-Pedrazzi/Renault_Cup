from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
app = Flask(__name__)
CORS(app)

# Configuración de Flask y BD
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/RenaultCup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

GMAIL_USER = "renaultcup0@gmail.com"
GMAIL_PASS = "ywer mdum zooi zvxm"

@login_manager.user_loader
def load_user(email):
    return Usuario.query.get(email)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'Cuenta_habilitada'
    Nombre = db.Column(db.String(100))
    Email = db.Column(db.String(100), unique=True, primary_key=True)
    Contraseña = db.Column(db.String(100))
    rango = db.Column(db.String(20))

    def get_id(self):
        return self.Email 
    
    def is_active(self):
        return True
    
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


class Verificacion(db.Model):
    __tablename__ = 'Verificacion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(40))
    codigo = db.Column(db.String(20))
    nombre = db.Column(db.String(40))
    contra_codificada = db.Column(db.String(200))
    rango = db.Column(db.String(20))

class Responsable(db.Model):
    __tablename__ = 'Responsable'
    
    id_profesor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_equipo = db.Column(db.Integer, db.ForeignKey('Equipo.id_equipo'), nullable=True)
    Nombre = db.Column(db.String(50), default='-')
    DNI = db.Column(db.String(10), nullable=True)
    Telefono = db.Column(db.String(15), nullable=True)
    Email = db.Column(db.String(40), nullable=True)
    Comida_especial = db.Column(db.String(3), default='N')
    Fecha_nacimiento = db.Column(db.Date, nullable=True)


@app.context_processor
def inject_user_rango():
    if current_user.is_authenticated:
        return dict(rango=current_user.rango)
    return dict()
    


@app.route("/check_email", methods=["POST"])
def check_email():
    data = request.get_json()
    email = data.get("Email")
    if not email:
        return jsonify({"exists": False})

    existe = Usuario.query.filter_by(Email=email).first() is not None or Verificacion.query.filter_by(email=email).first() is not None
    return jsonify({"exists": existe})

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    nombre = data.get("Nombre")
    email = data.get("Email")
    contraseña = data.get("Contraseña")
    rango = "A"
    usuario = Usuario.query.filter_by(Email=email).first()
    if not (nombre and email and contraseña):
        return jsonify({"success": False, "error": "Faltan datos"}), 400

    if usuario:
        if not usuario or not check_password_hash(usuario.Contraseña, contraseña):
            return jsonify({"success": False, "error": "El email ya está registrado y contraseña incorrecta"}), 401
        login_user(usuario)
        return jsonify({"success": False, "error": "El email ya está registrado"}), 400
    if Verificacion.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "El email ya está pendiente de verificacion"}), 400
    contra_codificada = generate_password_hash(contraseña)
    codigo = ''.join(random.choices('0123456789', k=6))

    verif = Verificacion(email=email, codigo=codigo, nombre=nombre, contra_codificada=contra_codificada, rango=rango)
    db.session.add(verif)
    db.session.commit()

    enviado = enviar_email(email, codigo)
    if not enviado:
        return jsonify({"success": False, "error": "No se pudo enviar el codigo de verificacion"}), 500

    return jsonify({"success": True, "mensaje": "Código enviado a tu email, verifica para activar tu cuenta."}), 200

@app.route("/verificar_codigo", methods=["POST"])
def verificar_codigo():
    data = request.get_json()
    email = data.get("Email")
    codigo = data.get("Codigo")

    if not (email and codigo):
        return jsonify({"success": False, "error": "Faltan datos"}), 400

    verif = Verificacion.query.filter_by(email=email).first()
    if not verif or verif.codigo != codigo:
        return jsonify({"success": False, "error": "Código incorrecto"}), 400


    usuario_existente = Usuario.query.filter_by(Email=email).first()
    if usuario_existente:
        return jsonify({"success": False, "error": "Usuario ya verificado"}), 400

    nuevo_usuario = Usuario(
        Nombre=verif.nombre,
        Email=verif.email,
        Contraseña=verif.contra_codificada,
        rango=verif.rango
    )
    db.session.add(nuevo_usuario)
    db.session.delete(verif)
    db.session.commit()

    login_user(nuevo_usuario)

    return jsonify({"success": True, "mensaje": "Cuenta verificada y sesión iniciada"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("Email")
    contraseña = data.get("Contraseña")

    if not (email and contraseña):
        return jsonify({"success": False, "error": "Faltan campos"}), 400

    usuario = Usuario.query.filter_by(Email=email).first()
    if not usuario or not check_password_hash(usuario.Contraseña, contraseña):
        return jsonify({"success": False, "error": "Contraseña incorrecta"}), 401

    login_user(usuario)
    return jsonify({"success": True, "usuario": {
        "Nombre": usuario.Nombre,
        "Email": usuario.Email
    }}), 200

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("Index"))

@app.route("/")
def Index():
    return render_template('Index.html')

@app.route("/signup", methods=["GET"])
def signup_page():
    return render_template('signup and login/signup.html')

@app.route("/login", methods=["GET"])
def login_page():
    return render_template('signup and login/login.html')
@app.route("/Add_Player")
def Create_Player():
    return render_template('Add/Add_Player.html')

@app.route("/Cantina")
def Cantina():
    return render_template('Add/Cantina.html')
@app.route("/Add_Equipo")
def hell():
    return render_template('Add/Add_Equipo.html')

@app.route("/Add_Match")
def Create_Match():
    return render_template('Add/Add_Match.html')

@app.route("/Add_Staff")
def Create_Staff():
    return render_template('Add/Add_Staff.html')

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
                'id_equipo': new_Equipo.id_equipo,
                'Colegio': new_Equipo.Colegio,
                'Deporte': new_Equipo.Deporte,
                'Sexo': new_Equipo.Sexo,
                'Categoria': new_Equipo.Categoria
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

@app.route('/api/Matches')
def get_matches():
    try:
        partidos = Partido.query.all()
        lista = []

        for partido in partidos:

            lista.append({
                "Fase": partido.Fase,
                "Arbitro": partido.Arbitro,
                "Planillero": partido.Planillero,
                "Equipo_1": partido.Equipo_1,
                "Equipo_2": partido.Equipo_2,
            })

        return jsonify(success=True, Matches=lista)

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/responsable', methods=['POST'])
def agregar_responsable():
    try:
        data = request.get_json()

        id_equipo = data.get('id_equipo') 
        Nombre = data.get('Nombre', '-')
        DNI = data.get('DNI')
        Telefono = data.get('Telefono')
        Email = data.get('Email')
        Comida_especial = data.get('Comida_especial', 'N')
        Fecha_nacimiento = data.get('Fecha_nacimiento') 

        fecha_obj = None
        if Fecha_nacimiento:
            from datetime import datetime
            try:
                fecha_obj = datetime.strptime(Fecha_nacimiento, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Formato de fecha inválido, debe ser YYYY-MM-DD'}), 400

        nuevo_responsable = Responsable(
            id_equipo=id_equipo,
            Nombre=Nombre,
            DNI=DNI,
            Telefono=Telefono,
            Email=Email,
            Comida_especial=Comida_especial,
            Fecha_nacimiento=fecha_obj
        )

        db.session.add(nuevo_responsable)
        db.session.commit()

        return jsonify({
            'success': True,
            'Responsable': {
                'id_profesor': nuevo_responsable.id_profesor,
                'Nombre': nuevo_responsable.Nombre,
                'DNI': nuevo_responsable.DNI,
                'Telefono': nuevo_responsable.Telefono,
                'Email': nuevo_responsable.Email,
                'Comida_especial': nuevo_responsable.Comida_especial,
                'Fecha_nacimiento': str(nuevo_responsable.Fecha_nacimiento),
                'id_equipo': nuevo_responsable.id_equipo
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/Equipos', methods=['GET'])
def get_equipos():
    equipos = Equipo.query.all()
    return jsonify([
        {
            'id': equipo.id_equipo,
            'colegio': equipo.Colegio,
            'deporte': equipo.Deporte,
            'sexo': equipo.Sexo,
            'categoria': equipo.Categoria
        }
        for equipo in equipos
    ])

@app.route('/api/Equipo/<int:id>', methods=['PUT'])
def update_equipo(id):
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({'success': False, 'error': 'Equipo no encontrado'}), 404
    data = request.get_json()
    try:
        equipo.Colegio = data['Colegio']
        equipo.Deporte = data['Deporte']
        equipo.Sexo = data['Sexo']
        equipo.Categoria = data['Categoria']
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/Equipo/<int:id>', methods=['DELETE'])
def delete_equipo(id):
    equipo = Equipo.query.get(id)
    if not equipo:
        return jsonify({'success': False, 'error': 'Equipo no encontrado'}), 404
    try:
        db.session.delete(equipo)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def enviar_email(destino, codigo):
    asunto = "Código de verificacion RenaultCup"
    cuerpo = f"Hola,\n\nTu codigo de verificacion es {codigo}"

    mensaje = MIMEMultipart()
    mensaje['From'] = GMAIL_USER
    mensaje['To'] = destino
    mensaje['Subject'] = Header(asunto, 'utf-8')  

    cuerpo_mime = MIMEText(cuerpo, 'plain', 'utf-8')
    mensaje.attach(cuerpo_mime)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        
        texto_email = mensaje.as_string()

        server.sendmail(GMAIL_USER, destino, texto_email)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

if __name__ == "__main__":
    app.run(debug=True)