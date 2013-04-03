from flask import Flask, render_template, request, abort, session, Response
import requests
import json
from redis import Redis

app = Flask(__name__, static_url_path='/static', static_folder='../app', template_folder='../app')
app.secret_key = 'topseekret'
redis = Redis()

def k(s):
    return 'pushapptophone:%s'%s

@app.route('/')
def index():
    endpointskey = k('%s:endpoints'%(session.get('email', '')))
    return render_template('index.html', email=session.get('email', None), devices=redis.lrange(endpointskey, 0, 20))

@app.route('/install', methods=['POST'])
def install():
    print request.form
    manifest = request.form['manifest']
    redis.set(k('manifest'), manifest)
    for endpoint in redis.lrange(k('%s:endpoints'%session['email']), 0, 25):
        print endpoint
        r = requests.put(endpoint)
        print r
    return ''

@app.route('/manifest')
def get_manifest():
    return Response(redis.get(k('manifest')), content_type='text/plain')

@app.route('/weblogin', methods=['POST'])
def weblogin():
    if 'assertion' not in request.form:
        abort(400)

    # Send the assertion to Mozilla's verifier service.
    data = {'assertion': request.form['assertion'], 'audience': 'http://pushtophone.nikhilism.com'}
    resp = requests.post('https://verifier.login.persona.org/verify', data=data, verify=True)
 
    # Did the verifier respond?
    if resp.ok:
        # Parse the response
        verification_data = json.loads(resp.content)
 
        # Check if the assertion was valid
        if verification_data['status'] == 'okay':
            # Log the user in by setting a secure session cookie
            session.update({'email': verification_data['email']})
            return verification_data['email']
        else:
            print 'status not okay', verification_data
    else:
        print 'resp.ok not true', resp
 
    # Oops, something failed. Abort.
    abort(500)

@app.route('/login', methods=['POST'])
def login():
    if 'assertion' not in request.form:
        abort(400)

    # Send the assertion to Mozilla's verifier service.
    data = {'assertion': request.form['assertion'], 'audience': 'system.gaiamobile.org'}
    resp = requests.post('https://verifier.login.native-persona.org/verify', data=data, verify=True)
 
    # Did the verifier respond?
    if resp.ok:
        # Parse the response
        verification_data = json.loads(resp.content)
 
        # Check if the assertion was valid
        if verification_data['status'] == 'okay':
            # Log the user in by setting a secure session cookie
            session.update({'email': verification_data['email']})
            return verification_data['email']
        else:
            print 'status not okay', verification_data
    else:
        print 'resp.ok not true', resp
 
    # Oops, something failed. Abort.
    abort(500)

@app.route('/endpoint', methods=['POST'])
def endpoint():
    endpoint = request.form['endpoint']
    email = request.form['email']

    print endpoint, email
    if not endpoint or not email:
        abort(400)

    redis.rpush(k('%s:endpoints'%email), endpoint)
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
