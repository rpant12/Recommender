import os
import spotipy

from flask import Flask, request, render_template
from flask_session import Session

from SpotifyRecommendation import overall as recommend
from SpotifyRecommendation import threshold as th

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
os.environ["SPOTIPY_CLIENT_ID"] = "c898dcfced6e454caa2e39746b99ee72"
os.environ["SPOTIPY_CLIENT_SECRET"] = "9bcbc3a05ea04ebbaf438f728e268bbc"
os.environ['SPOTIPY_REDIRECT_URI'] = "http://localhost:3000"
Session(app)


@app.route('/', methods=["GET", "POST"])
def home():  # put application's code here
	# t1 = Thread(target = task)
	# cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
	auth_manager = spotipy.oauth2.SpotifyOAuth(
		scope=["user-read-private", "user-read-email", 'user-top-read', "user-follow-read", "playlist-read-private",
		       "playlist-read-collaborative", "user-library-read", "user-follow-modify", "user-read-recently-played",
		       "user-read-playback-position"],
		show_dialog=True)

	# if request.args.get("code"):
	# 	# Step 2. Being redirected from Spotify auth page
	# 	auth_manager.get_access_token(request.args.get("code"))
	# 	return redirect('/  ')
	#
	# if not auth_manager.validate_token(cache_handler.get_cached_token()):
	# 	# Step 1. Display sign in link when no token
	# 	auth_url = auth_manager.get_authorize_url()
	# 	return f'<h2><a href="{auth_url}">Sign in</a></h2>'

	if request.method == "POST":
		genre = request.form.get("genre")
		return recommend(genre, th)
	return render_template("index.html")


if __name__ == '__main__':
	app.run(threaded=True, port=int(os.environ.get("PORT",
	                                               os.environ.get("SPOTIPY_REDIRECT_URI", 5000).split(":")[-1])))
