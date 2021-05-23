import logging
import json
import secrets
from datetime import datetime, timedelta

from flask import Flask, flash, redirect, render_template, Response, request, session, url_for
from flask_wtf.csrf import CSRFProtect
from pythonjsonlogger.jsonlogger import JsonFormatter
from spotify_client import Config, SpotifyClient

import config
from forms import AddSongToQueueForm


app_logger = logging.FileHandler(filename='app.log')
json_formatter = JsonFormatter(fmt='%(levelname)s %(asctime)s %s(pathname)s %(lineno)s %(name)s %(message)s')

spotify_logger_handler = app_logger
spotify_logger_handler.setFormatter(json_formatter)

app_logger_handler = app_logger
app_logger_handler.setFormatter(json_formatter)

spotify_logger = logging.getLogger('spotify_client')
spotify_logger.setLevel(logging.INFO)
spotify_logger.addHandler(spotify_logger_handler)

app_logger = logging.getLogger('spotifydj')
app_logger.setLevel(logging.INFO)
app_logger.addHandler(app_logger_handler)

csrf_logger = logging.getLogger('flask_wtf.csrf')
csrf_logger.setLevel(logging.INFO)
csrf_logger.addHandler(app_logger_handler)

app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY
csrf = CSRFProtect(app)


Config.configure(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET)
spotify_client = SpotifyClient()


@app.route('/login')
def login():
    state = secrets.token_urlsafe(config.SPOTIFY_SESSION_STATE_LENGTH)

    spotify_oauth_link = spotify_client.build_spotify_oauth_confirm_link(
        state=state,
        scopes=['user-modify-playback-state'],
        redirect_url=config.SPOTIFY_REDIRECT_URI
    )

    session['state'] = state

    return render_template('login.html', spotify_oauth_link=spotify_oauth_link)


@app.route('/auth')
def auth():
    request_state = request.args.get('state')
    session_state = session.get('state')

    if session_state and secrets.compare_digest(request_state, session_state):
        code = request.args.get('code')
        data = spotify_client.get_access_and_refresh_tokens(code, config.SPOTIFY_REDIRECT_URI)

        data.update({
            'last_refreshed': datetime.now().isoformat()
        })

        with open(config.SPOTIFY_CREDENTIALS_FILE, 'w') as fp:
            json.dump(data, fp)

        return redirect(url_for('add'))
    else:
        return Response('Invalid state parameter', status=400)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddSongToQueueForm()

    if request.method == 'GET':
        return render_template('add.html', form=form)
    elif request.method == 'POST':
        uri = form.uri.data

        with open(config.SPOTIFY_CREDENTIALS_FILE) as fp:
            creds = json.load(fp)

        last_refreshed = datetime.strptime(creds['last_refreshed'], "%Y-%m-%dT%H:%M:%S.%f")

        if last_refreshed <= datetime.now() - timedelta(hours=1):
            access_token = spotify_client.refresh_access_token(creds['refresh_token'])

            creds.update({
                'access_token': access_token,
                'refresh_token': creds['refresh_token'],
                'last_refreshed': datetime.now().isoformat()
            })

            with open(config.SPOTIFY_CREDENTIALS_FILE, 'w') as fp:
                json.dump(creds, fp)

        spotify_client.add_track_to_user_queue(creds['access_token'], uri)

        flash('Added song to queue!')

        return redirect(url_for('add'))


if __name__ == '__main__':
    app.run(debug=True)
