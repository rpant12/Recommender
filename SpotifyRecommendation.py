import string

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tabulate import tabulate

client_id = "c898dcfced6e454caa2e39746b99ee72"
client_secret = "9bcbc3a05ea04ebbaf438f728e268bbc"
redirect_uri = "http://localhost:3000"



def byGenre(row, genre):
    if genre.lower() in " ".join(row["genre"]):
        return True
    return False


def getUserSongs():
    scope = ["user-read-private", "user-read-email", 'user-top-read', "user-follow-read", "playlist-read-private",
             "playlist-read-collaborative", "user-library-read", "user-follow-modify", "user-read-recently-played",
             "user-read-playback-position"]

    client_id = "c898dcfced6e454caa2e39746b99ee72"
    client_secret = "9bcbc3a05ea04ebbaf438f728e268bbc"
    redirect_uri = 'http://localhost:3000'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret,
                                                   redirect_uri=redirect_uri))
    results = sp.current_user_recently_played(limit=50)
    isSaved = []
    savedID = []
    j = 0
    while True:
        try:
            saved = sp.current_user_saved_tracks(limit=50, offset=j)
            print(saved["items"][0]["track"]["name"])
            for item in saved["items"]:
                isSaved.append(item["track"]["name"])
                savedID.append(item["track"]["id"])
            j += 50
        except:
            print("songs found")
            break

    ids = []
    names = []
    artists = []
    year = []
    songSaved = []
    imgs = []

    for song in results["items"]:
        imgs.append(song["track"]["album"]["images"][0]["url"])
        ids.append(song["track"]["id"])
        names.append(song["track"]["name"])
        artists.append(song["track"]["album"]["artists"][0]["name"])
        year.append(int(song["track"]["album"]["release_date"].split("-")[0]))
        if song["track"]["name"] in isSaved:
            songSaved.append(True)
        else:
            songSaved.append(False)

    features = sp.audio_features(tracks=ids)
    features_df = pd.DataFrame()
    dance = []
    energy = []
    key = []
    loud = []
    speech = []
    acoustic = []
    instrumental = []
    live = []
    valence = []
    tempo = []
    duration = []
    time = []

    for item in features:
        dance.append(item["danceability"])
        energy.append(item["energy"])
        key.append(item["key"])
        loud.append(item["loudness"])
        speech.append(item["speechiness"])
        acoustic.append(item["acousticness"])
        instrumental.append(item["instrumentalness"])
        live.append(item["liveness"])
        valence.append(item["valence"])
        tempo.append(item["tempo"])
        duration.append(item["duration_ms"])
        time.append(item["time_signature"])

    ids = []
    for item in results["items"]:
        ids.append(item["track"]["artists"][0]["id"])

    gens = []
    for item in ids:
        genres = sp.artist(item)["genres"]
        if len(genres) == 0:
            gens.append(["None"])
        else:
            gens.append(genres)

    features_df["name"] = names
    features_df["artist"] = artists
    features_df["dance"] = dance
    features_df["energy"] = energy
    features_df["key"] = key
    features_df["loud"] = loud
    features_df["speech"] = speech
    features_df["acoustic"] = acoustic
    features_df["instrumental"] = instrumental
    features_df["live"] = live
    features_df["valence"] = valence
    features_df["tempo"] = tempo
    features_df["duration"] = duration
    features_df["time"] = time
    features_df["year"] = year
    features_df["saved"] = songSaved
    features_df["genre"] = gens
    features_df["image"] = imgs
    return features_df, savedID


def getGenreStats(genre, songs):
    feat = songs[songs.apply(byGenre, args = (genre,), axis = 1)]
    isSaved = feat[feat.get("saved")]
    notSaved = feat[~feat.get("saved")]
    compare = 0
    if isSaved.shape[0] == 0:
        compare =  notSaved.median(numeric_only = True)
    elif notSaved.shape[0] == 0:
        compare = isSaved.median(numeric_only = True)
    else:
        compare = isSaved.median(numeric_only = True) * 2/3 + notSaved.median(numeric_only = True) * 1/3
    return compare



def getGenre(genre, songs):
    feat = songs[songs.apply(byGenre, args = (genre,), axis = 1)]
    return feat



threshold = {
    "dance": 0.25,
    "energy": 0.25,
    "key": 6, 
    "loud": 5,
    "speech": 0.25,
    "acoustic": 0.25,
    "instrumental": 0.25,
    "live": 0.25,
    "valence": 0.2,
    "duration": 60000.0,
    "time": 2,
}


def validSong(row, stats, threshold):
    for metric in threshold.keys():
        if abs(row[metric] - stats[metric]) > threshold[metric]:
            return False
    return True


def getPreds(genre, songs, savedID):
    scope = ["user-read-private", "user-read-email", 'user-top-read', "user-follow-read", "playlist-read-private", "playlist-read-collaborative", "user-library-read", "user-follow-modify"]

    client_id = "c898dcfced6e454caa2e39746b99ee72"
    client_secret = "9bcbc3a05ea04ebbaf438f728e268bbc"
    redirect_uri = "http://localhost:3000"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri))
    playIDs = []
    plays = sp.search(q = genre, type = "playlist")["playlists"]["items"]
    for play in plays:
        playIDs.append(play["id"])

    playTracks = []
    for playID in playIDs:
        playlist = sp.playlist(playID)
        section = []
        try:
            section = playlist["tracks"]["items"][0:50]
        except:
            section = playlist["tracks"]["items"][0:20]
        for track in section:
            try:
                trackID = track["track"]["id"]
                if trackID not in playTracks and trackID not in savedID:
                    playTracks.append(trackID)
            except:
                pass

    j = 0
    overall = pd.DataFrame()

    for i in range((len(playTracks) // 50) + 1):
        pt = playTracks[j: j + 50]
        track_items = sp.tracks(pt)
        track_names = []
        track_artists = []
        track_year = []
        ids = []
        imgs = []
        for track in track_items["tracks"]:
            try:
                track_names.append(track["name"])
            except:
                track_names.append("None")
            try:
                track_artists.append(track["artists"][0]["name"])
            except:
                track_artists.append("None")
            try:
                track_year.append(track["album"]["release_date"].split("-")[0])
            except:
                track_year.append("None")
            try:
                ids.append(track["id"])
            except:
                ids.append("None")
            try:
                imgs.append(track["album"]["images"][0]["url"])
            except:
                imgs.append("None")

        track_features = sp.audio_features(pt)

        track_dance = []
        track_energy = []
        track_key = []
        track_loud = []
        track_speech = []
        track_acoustic = []
        track_instrumental = []
        track_live = []
        track_valence = []
        track_tempo = []
        track_duration = []
        track_time = []
        trackDF = pd.DataFrame()

        for item in track_features:
            try:
                track_dance.append(item["danceability"])
            except:
                track_dance.append(songs.dance.median())
            try:
                track_energy.append(item["energy"])
            except:
                track_energy.append(songs.energy.median())
            try:
                track_key.append(item["key"])
            except:
                track_key.append(songs.key.median())
            try:
                track_loud.append(item["loudness"])
            except:
                track_loud.append(songs.loud.median())
            try:
                track_speech.append(item["speechiness"])
            except:
                track_speech.append(songs.speech.median())
            try:
                track_acoustic.append(item["acousticness"])
            except:
                track_acoustic.append(songs.acoustic.median())
            try:
                track_instrumental.append(item["instrumentalness"])
            except:
                track_instrumental.append(songs.instrumental.median())
            try:
                track_live.append(item["liveness"])
            except:
                track_live.append(songs.live.median())
            try:
                track_valence.append(item["valence"])
            except:
                track_valence.append(songs.valence.median())
            try:
                track_tempo.append(item["tempo"])
            except:
                track_tempo.append(songs.tempo.median())
            try:
                track_duration.append(item["duration_ms"])
            except:
                track_duration.append(songs.duration.median())
            try:
                track_time.append(item["time_signature"])
            except:
                track_time.append(songs.time.median())

        trackDF["name"] = track_names
        trackDF["artist"] = track_artists
        trackDF["id"] = ids
        trackDF["image"] = imgs
        trackDF["dance"] = track_dance
        trackDF["energy"] = track_energy
        trackDF["key"] = track_key
        trackDF["loud"] = track_loud
        trackDF["speech"] = track_speech
        trackDF["acoustic"] = track_acoustic
        trackDF["instrumental"] = track_instrumental
        trackDF["live"] = track_live
        trackDF["valence"] = track_valence
        trackDF["tempo"] = track_tempo
        trackDF["duration"] = track_duration
        trackDF["time"] = track_time
        trackDF["year"] = track_year
        trackDF["isValid"] = trackDF.apply(validSong, args = (getGenreStats(genre, songs), threshold ), axis = 1)
        chosen = trackDF[trackDF.get("isValid")]
        overall = pd.concat([overall, chosen])
        j += 50
    overall = overall.drop_duplicates("name")
    return overall



def createPlay(preds, genre):
    scope = ["user-read-private", "user-read-email", 'user-top-read', "user-follow-read", "playlist-read-private", "playlist-read-collaborative", "user-library-read", "user-follow-modify", "playlist-modify-public", "playlist-modify-private"]

    client_id = "c898dcfced6e454caa2e39746b99ee72"
    client_secret = "9bcbc3a05ea04ebbaf438f728e268bbc"
    redirect_uri = "http://localhost:3000"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri))
    
    play_name = string.capwords(genre) + " Recommended Playlist by Raghav"
    play_desc = "This is a playlist created for you based off of the songs you've listened to!"
    sp.user_playlist_create(user = sp.current_user()["id"], name = play_name, public = False, collaborative = False, description = play_desc)
    return play_name


def addSongs(play_name, preds):
    scope = ["user-read-private", "user-read-email", 'user-top-read', "user-follow-read", "playlist-read-private", "playlist-read-collaborative", "user-library-read", "user-follow-modify", "playlist-modify-public", "playlist-modify-private"]

    client_id = "c898dcfced6e454caa2e39746b99ee72"
    client_secret = "9bcbc3a05ea04ebbaf438f728e268bbc"
    redirect_uri = "http://localhost:3000"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri))
    plays = sp.current_user_playlists(limit = 5)
    playID = plays["items"][0]["id"]
    ids = preds.id
    sp.playlist_add_items(playlist_id = playID, items = ids)
    return plays["items"][0]["external_urls"]["spotify"]


def sim_score(row, stats):
    score = 0
    for metric in stats.keys():
        try:
            score += abs(row[metric] - stats[metric])
        except:
            continue
    return score


def overall(genre, threshold):
    songs, saved = getUserSongs()
    print("Gotten Songs")
    stats = getGenreStats(genre, songs)
    ask = ""
    if getGenre(genre, songs).shape[0] == 0:
        ask = input("There are no songs of this genre in your 50 recently played songs, "
                    + "do you want to continue? (Y/N)")
        if ask.upper() != "Y":
            return "Stopped"
    preds = getPreds(genre, songs, saved)
    print("Created Predictions")
    preds["score"] = preds.apply(sim_score, args = (stats, ), axis = 1)
    preds = preds.sort_values("score", ascending = True).reset_index(drop = True)[0:50]
    preds = preds[preds.get("name") != '']
    name = createPlay(preds, genre)
    print("Created Playlist")
    pLink = addSongs(name, preds)
    print("Added Songs")
    songs = "<!doctype html>" \
            "<html lang='en'>" \
            "<head>" \
            "<title>Your Recommended Playlist</title>" \
            "<meta charset='utf-8'>" \
            "<meta name='viewport' content='width=device-width, initial-scale=1, shrink-to-fit=no'>" \
            "<link href='https://fonts.googleapis.com/css?family=Poppins:300,400,500,600,700,800,900' rel='stylesheet'>" \
            "<link rel='stylesheet' href='static/styles/owl.carousel.min.css'>" \
            "<link rel='stylesheet' href='static/styles/owl.theme.default.min.css'>" \
            "<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/ionicons/4.5.6/css/ionicons.min.css'>" \
            "<link rel='stylesheet' href='static/styles/style.css'>" \
            "</head>" \
            "<body>" \
            "<div class='home-slider owl-carousel js-fullheight'>"
    for i in range(preds.shape[0]):
        songs += "<div class='slider-item js-fullheight' style='background-image:url("+ preds.iloc[i].get("image") + ");'>" \
            "<div class='overlay'></div>" \
            "<div class='container'>" \
            "<div class='row no-gutters slider-text js-fullheight align-items-center justify-content-center'>" \
            "<div class='col-md-12 ftco-animate'>" \
            "<div class='text w-100 text-center'>" \
            "<a href='" + pLink + "'>" \
            "<h1 class = 'mb-3'>" + preds.iloc[i].get("name") + "</h2>" \
            "<h2> by " + preds.iloc[i].get("artist") + "</h1>" \
            "</a> </br>" \
            "<h4 class = 'mt-3'> Click on the song to go to the playlist! </h4>" \
            "</div>" \
            "</div>" \
            "</div>" \
            "</div>" \
            "</div>" \

    songs += "</div>" \
            "<script src='static/js/jquery.min.js'></script>" \
            "<script src='static/js/popper.js'></script>" \
            "<script src='static/js/bootstrap.min.js'></script>" \
            "<script src='static/js/owl.carousel.min.js'></script>" \
            "<script src='static/js/main.js'></script>" \
            "</body>" \
            "</html>"
    return songs



