from flask import Flask, render_template, request,jsonify,flash,redirect,url_for
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy import inspect
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password1234@localhost/RenaultCup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

class Jugador(db.Model):
    __tableNombre__ = 'Jugador'  
    id= db.Column(db.Integer, primary_key=True)
    Nombre= db.Column(db.String(100))
    id_equipo = db.Column(db.Integer)
    DNI= db.Column(db.String(20))
    Telefono=db.Column(db.String(20))
    Email= db.Column(db.String(100))
    Fecha_nacimiento = db.Column(db.String(100))
    Comida_Especial = db.Column(db.String(100))

class Equipo(db.Model):
    __tableNombre__ = 'Equipo'  
    id_equipo= db.Column(db.Integer, primary_key=True)
    Colegio= db.Column(db.String(50))
    Deporte = db.Column(db.String(10))
    Sexo= db.Column(db.String(10))
    Categoria=db.Column(db.String(10))

class Partido(db.Model):
    __tableNombre__ = 'Partido'
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

class User(UserMixin,db.Model):
    __tablename__ = 'Cuenta_habilitada' 
    id_cuenta= db.Column(db.Integer, primary_key=True)
    Nombre= db.Column(db.String(40))
    Contraseña= db.Column(db.String(20))
    Email= db.Column(db.String(40))
    Rango= db.Column(db.String(20))


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(tables)

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def validate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None
@app.route("/signup", methods=["POST"])
def Signup():
    try:
        data = request.get_json()

        Nombre = data.get('Nombre')
        Email = data.get('Email')
        Contraseña = data.get('Contraseña')
        Rango = "C"  

        if not (Nombre and Email and Contraseña):
            return jsonify({'success': False, 'error': 'Faltan campos requeridos'}), 400

        if User.query.filter_by(Nombre=Nombre).first():
            return jsonify({'success': False, 'error': 'El nombre de usuario ya existe'}), 409
        if User.query.filter_by(Email=Email).first():
            return jsonify({'success': False, 'error': 'El email ya está en uso'}), 409

        new_user = User(Nombre=Nombre, Email=Email, Rango=Rango)
        new_user.set_password(Contraseña)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'success': True,
            'Jugador': {
                'Nombre': new_user.Nombre,
                'email': new_user.Email
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/Count")
def signup():
    return render_template('signup.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
    


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.validate(username, password)
        if user:
            login_user(user)
            flash("Logged in successfully!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Hello, {current_user.username}!"

@app.route("/logout")
@login_required
def logout():
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
    

