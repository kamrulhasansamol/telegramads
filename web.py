from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import requests
import json

# ================= SETTINGS =================
BASE_API = os.environ.get('BASE_API', 'http://104.234.236.62:30151')
HERE = os.path.dirname(os.path.abspath(__file__))
EMOTE_DIR = os.path.join(HERE, 'emote')
CATEGORIES_FILE = os.path.join(HERE, 'categories.json')

app = Flask(__name__, template_folder='templates', static_folder='static')


# ================= FRONT PAGE =================
@app.route('/')
def index():
    try:
        if os.path.exists(EMOTE_DIR):
            files = [f for f in os.listdir(EMOTE_DIR) if f.lower().endswith('.png')]
        else:
            files = []
    except Exception as e:
        print(f"Error reading emote dir: {e}")
        files = []
    files.sort()

    categories = []
    try:
        if os.path.exists(CATEGORIES_FILE):
            with open(CATEGORIES_FILE, 'r', encoding='utf-8') as cf:
                cat_data = json.load(cf)
                categories = cat_data.get('categories', [])
        else:
            raise FileNotFoundError("categories.json not found")
    except Exception as e:
        print(f"Error loading categories: {e}")
        categories = [
            {"name": "All", "emotes": []},
            {"name": "EVO", "emotes": ["909033", "909034", "909035"]},
            {"name": "Default", "emotes": ["909000"]}
        ]

    return render_template('index.html', emotes=files, categories=categories)


# ================= SERVE EMOTE FILES =================
@app.route('/emote_files/<path:filename>')
def emote_files(filename):
    return send_from_directory(EMOTE_DIR, filename)


# ================= JOIN =================
@app.route('/api/join', methods=['POST'])
def api_join():
    data = request.get_json() or request.form
    uid1 = data.get('uid1')
    emote_id = data.get('emote_id')
    team_code = data.get('teamcode') or data.get('tc')

    if not uid1:
        return jsonify({'error': 'uid1 required'}), 400
    if not emote_id:
        return jsonify({'error': 'emote_id required'}), 400
    if not team_code:
        return jsonify({'error': 'teamcode required'}), 400

    params = {
        'uid1': uid1,
        'emote_id': emote_id,
        'tc': team_code
    }

    try:
        r = requests.get(f"{BASE_API}/join", params=params, timeout=10)
        return (r.text, r.status_code, {'Content-Type': r.headers.get('Content-Type', 'text/plain')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================= LEAVE =================
@app.route('/api/leave', methods=['POST'])
def api_leave():
    try:
        r = requests.get(f"{BASE_API}/leave", timeout=10)
        return (r.text, r.status_code, {'Content-Type': r.headers.get('Content-Type', 'text/plain')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================= EMOTE =================
@app.route('/api/emote', methods=['POST'])
def api_emote():
    data = request.get_json() or request.form
    emote_id = data.get('emote_id')
    team_code = data.get('teamcode') or data.get('tc')

    # Collect up to 6 UIDs
    uid_list = []
    for i in range(1, 7):
        v = data.get(f'uid{i}')
        if v:
            uid_list.append(v)

    if not emote_id:
        return jsonify({'error': 'emote_id required'}), 400
    if not team_code:
        return jsonify({'error': 'teamcode required'}), 400
    if not uid_list:
        return jsonify({'error': 'at least one uid required'}), 400

    params = {'emote_id': emote_id, 'tc': team_code}
    for i, uid in enumerate(uid_list[:6], start=1):
        params[f'uid{i}'] = uid

    try:
        r = requests.get(f"{BASE_API}/emote", params=params, timeout=10)
        return (r.text, r.status_code, {'Content-Type': r.headers.get('Content-Type', 'text/plain')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================= FAST EMOTE =================
@app.route('/api/fastemote', methods=['POST'])
def api_fastemote():
    data = request.get_json() or request.form
    team_code = data.get('teamcode') or data.get('tc')
    emote_id = data.get('emote_id') or data.get('emoteid')
    uid1 = data.get('uid1')
    uid2 = data.get('uid2')
    uid3 = data.get('uid3')

    if not team_code:
        return jsonify({'error': 'teamcode (tc) required'}), 400
    if not emote_id:
        return jsonify({'error': 'emote_id required'}), 400

    params = {'tc': team_code, 'emoteid': emote_id}
    if uid1: params['uid1'] = uid1
    if uid2: params['uid2'] = uid2
    if uid3: params['uid3'] = uid3

    try:
        r = requests.get(f"{BASE_API}/fast", params=params, timeout=15)
        return (r.text, r.status_code, {'Content-Type': r.headers.get('Content-Type', 'text/plain')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================= MAIN =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)
