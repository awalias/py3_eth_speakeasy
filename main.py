
import uuid
import json
from flask import Flask, render_template, send_from_directory, request
from flask_socketio import SocketIO
import web3
from eth_account.messages import defunct_hash_message
from google.cloud import datastore

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__, template_folder='./templates', static_url_path='')
app.config['SECRET_KEY'] = 'bnkd2nfjknfl1232#'
socketio = SocketIO(app)

CURRENT_APP_VERSION = "index"

# setup some clients
w3 = web3.Web3(web3.Web3.HTTPProvider("https://mainnet.infura.io/v3/60ae97a8fe984792b849ef1d047d295a"))
db = datastore.Client()

@app.route('/')
def index():
    """Return a homepage."""

    return render_template(
        'index.html',
        CURRENT_APP_VERSION = CURRENT_APP_VERSION,
    )


@app.route('/auth', methods=['POST'])
def auth():
    step = request.form.get('step')

    if step == 'init':
        eth_address = request.form.get('eth_address')

        user_key = db.key('Users', eth_address)
        user = db.get(user_key)

        if user:
            # generate nonce and return it to user
            new_nonce = generate_new_nonce()
            user.update({
                'nonce': new_nonce,
            })
            db.put(user)
            return json.dumps({'nonce' : new_nonce })

        else:
            # create new user - generate nonce and return it to user
            new_nonce = generate_new_nonce()
            user = datastore.Entity(key=user_key)
            user.update({
                'nonce': new_nonce,
            })
            db.put(user)
            return json.dumps({'nonce' : new_nonce })


    elif step == 'auth':
        eth_address = request.form.get('eth_address')
        signed_nonce = request.form.get('signed_nonce')

        user_key = db.key('Users', eth_address)
        user = db.get(user_key)

        if not user:
            return json.dumps({'success':False, 'message':"You are not authorised 1"})

        else:
            verified = verify_sig(user.get('nonce'), signed_nonce, eth_address)
            has_sufficient_balance = w3.fromWei(w3.eth.getBalance(eth_address), 'ether') >= 32

            if verified and has_sufficient_balance:
                # TODO send chat page
                return json.dumps({'success':True, 'message':render_template('session.html')})
            else:
                return json.dumps({'success':False, 'message':"You are not authorised 2"})


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)


def verify_sig(nonce, signed_nonce, eth_address):
    # verify sig
    msg_hash = defunct_hash_message(text="ETH Speakeasy Login code: " + nonce)
    recovered_address = w3.eth.account.recoverHash(msg_hash, signature=signed_nonce)

    return recovered_address == eth_address


def generate_new_nonce():
    return uuid.uuid4().hex


@app.route('/static/<path:path>')
def forward_static(path):
    return send_from_directory('static', path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static/images', path)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    #app.run(host='127.0.0.1', port=8080, debug=True)
    socketio.run(app, debug=True)
