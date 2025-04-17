from flask import Flask, request, jsonify, Response, send_from_directory
from flask_compress import Compress
from pp7_api import stage, timer, sse_clients, dispatcher
import json
import socket
import os
from auth import bake_cookie, authorise

host = ""
port = ""

with open('info.json', 'r') as config_file:
    config = json.load(config_file)
    host = config["host"]
    port = int(config["port"])

stage = stage.Stage(host, port)
timer = timer.Timer(host, port)

clients = []

def make_stream(filtre_type):
    def event_stream():
        client = {'filtre': filtre_type}
        clients.append(client)
        timer = 0
        try:
            while True:
                dispatcher.ready_data
                data = dispatcher.ready_data[filtre_type]
                if data:
                    if data['timer/system_time'] ==  timer:
                        yield ": ping\n\n"
                        continue
                    yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            clients.remove(client)

    return Response(event_stream(), mimetype='text/event-stream')

app = Flask(__name__, static_folder='public')
Compress(app)
PUBLIC_DIR = os.path.join(os.getcwd(), 'public')

@app.before_request
def check_token():
    exempt_routes = ['login']

    if request.endpoint in exempt_routes:
        return

    auth_header = request.headers.get('Authorization')

    if not auth_header or not authorise(auth_header.replace('Bearer ', '', 1)):
        return redirect(url_for('login'))


@app.route('/api/stage/msg', methods=['PUT'])
def stage_send_msg():
    data = request.get_json()
    msg = data.get('user_input')
    print(msg)
    result = stage.send_msg(msg)
    return jsonify({'result': result})

@app.route('/api/stage/msg', methods=['DELETE'])
def stage_delete_msg():
    result = stage.delete_msg()
    return jsonify({'result': result})

@app.route('/api/timer/play/<string:uuid>', methods=['GET'])
def play_timer(uuid):
    result = timer.play(uuid)
    return jsonify({'result': result})

@app.route('/api/timer/pause/<string:uuid>', methods=['GET'])
def pause_timer(uuid):
    result = timer.pause(uuid)
    return jsonify({'result': result})

@app.route('/api/timer/reset/<string:uuid>', methods=['GET'])
def reset_timer(uuid):
    result = timer.reset(uuid)
    return jsonify({'result': result})

@app.route('/api/timer/<string:uuid>', methods=['DELETE'])
def delete_timer(uuid):
    result = timer.delete(uuid)
    return jsonify({'result': result})

@app.route('/api/timer/<string:uuid>', methods=['PUT'])
def modify_timer(uuid):
    result = timer.modify(uuid)
    return jsonify({'result': result})

@app.route('/api/timer', methods=['POST'])
def post_timer():
    data = request.get_json()
    result = timer.post(data)
    return jsonify({'result': result})

@app.route('/api/joke', methods=['GET'])
def joke():
    request = json.dumps({
        "url": "v1/find_my_mouse",
        "method": "GET"
    }, separators=(',', ':')) + "\r\n"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, int(port)))
            except Exception as e:
                print("Impossible de se connecter:", e)

            s.send(request.encode('utf-8'))
            response = s.recv(1024)
            print(response)
            if response:
                return jsonify({'result': 'True'})
            else:
                print(f'Échec de la requête Joke. Code de statut : {response.status_code}')
                return jsonify({'result': 'False'})
    except Exception as e:
            print(f'Erreur lors de l\'envoi du message: {e}')
            return False

@app.route('/api/prompt')
def prompt_stream():
    return make_stream('prompt')

@app.route('/api/sub')
def sub_stream():
    return make_stream('sub')

@app.route('/api/status')
def status_stream():
    return make_stream('status')

@app.route('/', methods=['GET'])
def serve_index():
    response = send_from_directory(PUBLIC_DIR, 'index.html')
    response.cache_control.max_age = 604800
    response.cache_control.public = True
    return response

@app.route('/subtitles', methods=['GET'])
def serve_sub():
    response = send_from_directory(PUBLIC_DIR, 'subtitles.html')
    response.cache_control.max_age = 604800
    response.cache_control.public = True
    return response

@app.route('/prompt', methods=['GET'])
def serve_prompt():
    response = send_from_directory(PUBLIC_DIR, 'prompteur.html')
    response.cache_control.max_age = 604800
    response.cache_control.public = True
    return response

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    response = send_from_directory(PUBLIC_DIR, path)
    response.cache_control.max_age = 604800
    response.cache_control.public = True
    return response

@app.errorhandler(400)
def bad_request(error):
    app.logger.error(f"Bad request: {request.data}")
    return jsonify({'message': 'Bad request'}), 400

app.config['COMPRESS_MIN_SIZE'] = 500

if __name__ == '__main__':
    sse_clients.start_api_stream(host, port)
    dispatcher.start_dispatcher()

    app.run(host='0.0.0.0', port=5000, debug=False)