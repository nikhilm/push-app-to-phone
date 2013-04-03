from flask import Flask, render_template, request, abort, session, Response
import requests
import json
from redis import Redis

app = Flask(__name__, static_url_path='/static', static_folder='../app', template_folder='../app')
redis = Redis()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/install', methods=['POST'])
def install():
    manifest = request.form['manifest']
    redis.set('pushapptophone:manifest', manifest)
    for endpoint in redis.lrange('pushapptophone:endpoints', 0, 25):
        print endpoint
        r = requests.put(endpoint)
        print r
    return ''

@app.route('/manifest')
def get_manifest():
    return Response(redis.get('pushapptophone:manifest'), content_type='text/plain')

@app.route('/login', methods=['POST'])
def login():
    if 'assertion' not in request.form:
        abort(400)

    # Send the assertion to Mozilla's verifier service.
    data = {'assertion': request.form['assertion'], 'audience': 'http://pushtophone.nikhilism.com'}
    resp = requests.post('https://verifier.login.native-persona.org/verify', data=data, verify=True)
 
    # Did the verifier respond?
    if resp.ok:
        # Parse the response
        verification_data = json.loads(resp.content)
 
        # Check if the assertion was valid
        if verification_data['status'] == 'okay':
            # Log the user in by setting a secure session cookie
            session.update({'email': verification_data['email']})
            return resp.content
        else:
            print 'status not okay', verification_data
    else:
        print 'resp.ok not true', resp
 
    # Oops, something failed. Abort.
    abort(500)

@app.route('/endpoint', methods=['POST'])
def endpoint():
    endpoint = request.form['endpoint']
    print endpoint
    if not endpoint:
        abort(400)

    redis.rpush('pushapptophone:endpoints', endpoint)
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
