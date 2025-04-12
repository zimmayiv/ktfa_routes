from flask import Flask, render_template, jsonify, request
import os, json

app = Flask(__name__)

GEOJSON_DIR = os.path.join(app.static_folder, "geojsons")

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

@app.route('/list')
def list_geojsons():
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
                file_urls[item] = sorted(files, reverse=True)
        return jsonify(file_urls)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit/<name>', methods=['POST'])
def edit(name):
    if request.form['password'] == 'test':
        return render_template('edit.html', name=name)
    else:
        return 'Invalid password. <a href="/">Go back.</a>'

@app.route('/save', methods=['POST'])
def save():
    content = request.get_json()
    filepath = 'static/geojsons/' + request.headers.get('route') + '/' + request.headers.get('filename')
    with open(filepath, 'w') as f:
        json.dump(content, f)
    return 'File saved!'

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
