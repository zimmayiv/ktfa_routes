from flask import Flask, render_template, jsonify, request
import os, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Table, desc
from datetime import date
import ast

database_url = os.environ.get('DATABASE_URL')

if database_url and database_url.startswith('postgres:'):
    database_url = database_url.replace('postgres:', 'postgresql:', 1)

# what's the heroku postgres url?
database_url = 'postgresql://yiv:postgres@localhost/postgres'

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)
GEOJSON_DIR = os.path.join(app.static_folder, "geojsons")

class Update(db.Model):
    __tablename__ = "route"
    geojson = db.Column(db.String(4096), unique=True,nullable=True)
    date = db.Column(db.Date, unique=False, nullable=False)
    route = db.Column(db.String(64), nullable=True, unique=False)
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False, unique=False)

migrate = Migrate(app, db)

legendColor = {
  '1st Baptist Church': '#ff7f50',
  'Lafayette Park': '#87cefa',
  'Oakwood Raiders': '#da70d6',
  'Olympic': '#32cd32',
  'Seoul Park': '#6495ed',
  'Shatto': '#ff69b4',
  "Sherin's Floater": '#ba55d3',
  '6th Street': '#cd5c5c',
  '8th Street': '#ffa500',
  'Parkview': '#40e0d0',
  'Juanita Raiders': '#5e802f'
}

# places you need to replace files by postgres:
# edit page
# routes page

def listGeojsons():
    try:
        # Get all .geojson files

        file_urls = {}
        for item in os.listdir(GEOJSON_DIR):
            subfolder_path = os.path.join(GEOJSON_DIR, item)
            if os.path.isdir(subfolder_path):
                files = [
                    f"/static/geojsons/{item}/{f}"
                    for f in os.listdir(subfolder_path)
                    if os.path.isfile(os.path.join(subfolder_path, f))
                    and f.lower().endswith(".geojson")
                ]
                file_urls[item] = files
            # sort files by modification time (most recent first)
            # files.sort(key=lambda f: os.path.getmtime(os.path.join(GEOJSON_DIR, f)), reverse=True) 
        return file_urls
    
    except Exception as e:
        return None

@app.route('/list', methods=['GET'])
def list():
    try:
        if request.args.get('route'):
            updates = Update.query.filter(Update.route == request.args.get('route')).order_by(desc(Update.date)).all()
            updatelist = [
                {
                    'geojson': ast.literal_eval(u.geojson),
                    'count': u.count,
                    'route': u.route,
                    'date': u.date.strftime("%B %-d, %Y")
                }
                for u in updates
            ]
            return jsonify(updatelist)
        else:
            result = {}
            for key in legendColor:
                updates = Update.query.filter(Update.route == key).order_by(desc(Update.date)).all()
                updatelist = [
                    { 
                        'geojson': ast.literal_eval(u.geojson),
                        'count': u.count,
                        'route': u.route,
                        'date': u.date.strftime("%B %-d, %Y")
                    }
                    for u in updates
                ]
                result[key] = updatelist
            return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit/<name>', methods=['POST'])
def edit(name):
    if request.form['password'] == 'test':
        return render_template('edit.html', name=name)
    else:
        return 'Invalid password. <a href="/">Go back.</a>'

@app.route('/save',methods=['POST'])
def save():
    geo = str(request.get_json())
    rname = request.headers.get('route')
    count = request.headers.get('count')
    try:
        new_update = Update(
            geojson=geo,
            date=date.today(), 
            route=rname,
            count=count
        )
        db.session.add(new_update)
        db.session.commit()
    except Exception as e:
        return str(e)
    return 'Route updated!'

@app.route('/')
def routes():
    return render_template('routes.html', list=listGeojsons(), legendColor=legendColor)

@app.route('/draw')
def draw():
    return render_template('draw.html')

@app.route('/base')
def base():
    return render_template('mapbase.html')

if __name__ == '__main__':
    app.run(debug=True)
