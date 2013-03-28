from flask import Flask, render_template, request, abort, session
import requests
import json

app = Flask(__name__, static_url_path='/static', static_folder='../app', template_folder='../app')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if 'assertion' not in request.form:
        abort(400)

    # Send the assertion to Mozilla's verifier service.
    data = {'assertion': request.form['assertion'], 'audience': 'https://localhost:5000'}
    resp = requests.post('https://verifier.login.persona.org/verify', data=data, verify=True)
 
    # Did the verifier respond?
    if resp.ok:
        # Parse the response
        verification_data = json.loads(resp.content)
 
        # Check if the assertion was valid
        if verification_data['status'] == 'okay':
            # Log the user in by setting a secure session cookie
            session.update({'email': verification_data['email']})
            return resp.content
 
    # Oops, something failed. Abort.
    abort(500)

if __name__ == '__main__':
    app.run(debug=True)
