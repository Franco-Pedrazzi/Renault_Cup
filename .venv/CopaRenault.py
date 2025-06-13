from flask import Flask, render_template, request,jsonify
from flask_sqlalchemy  import SQLAlchemy
from sqlalchemy import inspect
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/RenaultCup'
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


with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(tables)

@app.route("/")
def Index():
    return render_template('Index.html')

@app.route("/Add Player")
def Create_Player():
    return render_template('Add_Player.html')

@app.route("/Add Equipo")
def hell():
    return render_template('Add_Equipo.html')

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

if __name__ == "__main__":
    app.run(debug=True)
    

