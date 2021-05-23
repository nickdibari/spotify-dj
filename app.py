import logging
import json
from datetime import datetime, timedelta

from flask import Flask, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from spotify_client import Config, SpotifyClient

import config
from forms import AddSongToQueueForm


logging.basicConfig(filename='app.log', level=logging.INFO)


app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY
csrf = CSRFProtect(app)


Config.configure(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET)
spotify_client = SpotifyClient()


@app.route('/login')
def login():
    spotify_oauth_link = spotify_client.build_spotify_oauth_confirm_link(
        state='12345',
        scopes=['user-modify-playback-state'],
        redirect_url=config.SPOTIFY_REDIRECT_URI
    )

    return render_template('login.html', spotify_oauth_link=spotify_oauth_link)


@app.route('/auth')
def auth():
    code = request.args.get('code')
    data = spotify_client.get_access_and_refresh_tokens(code, config.SPOTIFY_REDIRECT_URI)

    data.update({
        'last_refreshed': datetime.now().isoformat()
    })

    with open(config.SPOTIFY_CREDENTIALS_FILE, 'w') as fp:
        json.dump(data, fp)

    return redirect(url_for('add'))


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

        return render_template('add.html', form=AddSongToQueueForm(formdata=None))


if __name__ == '__main__':
    app.run(debug=True)
