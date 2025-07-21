from flask import Flask, render_template, jsonify, request, make_response
from flask_talisman import Talisman
import os, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Table, desc
from datetime import date
import ast

is_prod = os.environ.get('IS_HEROKU', None)
database_url = os.environ.get('DATABASE_URL', 'postgresql://yiv:postgres@localhost/postgres')

if database_url and database_url.startswith('postgres:'):
    database_url = database_url.replace('postgres:', 'postgresql:', 1)

app = Flask(__name__)
talisman = Talisman(app)

# Content Security Policy (CSP) Header
csp = {
    'default-src': ["'self'", 
                   'https://unpkg.com',
                   'https://cdnjs.cloudflare.com/',
                   "'unsafe-inline'",
                   'https://*.openstreetmap.org']
}
talisman.force_https = True
talisman.content_security_policy = csp


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)

if is_prod:
    accessword = os.environ.get('ACCESSWORD', None)
    password = os.environ.get('PASSWORD', None)
else:
    accessword = 'test'
    password = 'test'

class Update(db.Model):
    __tablename__ = "route"
    geojson = db.Column(db.String(32768), unique=True,nullable=True)
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

@app.before_request
def check_specialk_cookie():
    if request.cookies.get('specialk') != accessword and request.path != '/':
        return make_response('sorry', 403)

@app.route('/counts')
def count():
    return_json = {}
    try:
        for route in legendColor.keys():
            last = Update.query.filter(Update.route == route).order_by(desc(Update.date)).first()
            if last:
                return_json[route] = {'count': last.count, 'date': last.date} 
    except Exception as e:
        return 'Error: ' + str(e)
    return jsonify(return_json), 500


def listem(route):
    try:
        if route:
            updates = Update.query.filter(Update.route == route).order_by(desc(Update.date)).all()
            updatelist = [
                {
                    'geojson': ast.literal_eval(u.geojson),
                    'count': u.count,
                    'route': u.route,
                    'date': u.date.strftime("%B %-d, %Y")
                }
                for u in updates
            ]
            return updatelist
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
            return result
    except Exception as e:
        raise e

@app.route('/list', methods=['GET'])
def list_api():
    try:
        if request.args.get('route'):
            return jsonify(listem(request.args.get('route')))
        else:
            return jsonify(listem(None))
    except Exception as e: 
        return jsonify({"error": str(e)}), 500


@app.route('/edit/<name>', methods=['POST'])
def edit(name):
    if request.form['password'] == password:
        return render_template('edit.html', name=name, data=listem(name))
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
    if request.cookies.get('specialk') != accessword:
        return '''
                <script>
                    const value = prompt("Who are you?");
                    document.cookie = "specialk=" + encodeURIComponent(value) + "; path=/";
                    location.reload();
                </script>
            '''
    return render_template('routes.html', legendColor=legendColor, data=listem(None))

@app.route('/draw')
def draw():
    return render_template('draw.html')

@app.route('/base')
def base():
    return render_template('mapbase.html')

@app.route('/trace/<name>', methods=['POST'])
def trace(name):
    if request.form['password'] == password:
        return render_template('trace.html', name=name)
    else:
        return 'Invalid password. <a href="/">Go back.</a>'

if __name__ == '__main__':
    app.run(debug=True)
