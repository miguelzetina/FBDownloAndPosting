from pytube import YouTube
from pytube.exceptions import PytubeError
import psycopg2
from psycopg2.errors import UniqueViolation
import os
from urllib import parse
from googleapiclient import discovery
from urllib.parse import parse_qs, urlparse
from random import choice
from convert_audio_to_video import convert

DB_URL = os.getenv('DATABASE_URL')

# DEFAULT_URL = parse.urlparse(DB_URL)
DEFAULT_URL = parse.urlparse("postgres://jzilhsobslcxmp:c250991a92a256edc357e8a60a5094e3263c24bbe9a1c58e84e474eb77710985@ec2-54-163-254-204.compute-1.amazonaws.com:5432/d8g16kbbf6antq")

AUDIO_DOWNLOAD_DIR = os.getenv('AUDIO_DOWNLOAD_DIR')

db_credentials = {
    'NAME': DEFAULT_URL.path[1:],
    'USER': DEFAULT_URL.username,
    'PASSWORD': DEFAULT_URL.password,
    'HOST': DEFAULT_URL.hostname,
    'PORT': DEFAULT_URL.port
}

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY') or "AIzaSyDCrDHr6LVvfTvbIcbhi_oxlJ5LfWHCGYg"

YOUTUBE_PLAYLIST_URL = os.getenv('YOUTUBE_PLAYLIST_URL') or \
                       'https://youtube.com/playlist?list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG'


def retrieve_videos_urls():
    # extract playlist id from url
    url = YOUTUBE_PLAYLIST_URL
    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    playlist_id = query["list"][0]

    print(f'get all playlist items links from {playlist_id}')
    youtube = discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    print(f"total: {len(playlist_items)}")

    # Example of a playlist item:
    # {'kind': 'youtube#playlistItem', 'etag': 'o5S5Xnr-6HCbvMCmhkVUSAgTae4',
    # 'id': 'UExJWWVsby1WZkhtOGw1R1hWMC1leHhVNWpKMlVmMmFjRy41NkI0NEY2RDEwNTU3Q0M2', 'snippet': {'publishedAt':
    # '2017-09-24T03:01:30Z', 'channelId': 'UCgxZKq924a1LIDQtMyIJqkA', 'title': 'Andrés Suárez - Luz de Pregonda (
    # Audio)', 'description': 'Music video by Andrés Suárez performing Luz de Pregonda (Audio). (C)2015 Sony Music
    # Entertainment España, S.L.\nhttp://www.vevo.com/watch/ES1021500178', 'thumbnails': {'default': {'url':
    # 'https://i.ytimg.com/vi/dAMo12gqYac/default.jpg', 'width': 120, 'height': 90}, 'medium': {'url':
    # 'https://i.ytimg.com/vi/dAMo12gqYac/mqdefault.jpg', 'width': 320, 'height': 180}, 'high': {'url':
    # 'https://i.ytimg.com/vi/dAMo12gqYac/hqdefault.jpg', 'width': 480, 'height': 360}, 'standard': {'url':
    # 'https://i.ytimg.com/vi/dAMo12gqYac/sddefault.jpg', 'width': 640, 'height': 480}, 'maxres': {'url':
    # 'https://i.ytimg.com/vi/dAMo12gqYac/maxresdefault.jpg', 'width': 1280, 'height': 720}}, 'channelTitle': 'Miguel
    # Angel Zetina Zetina', 'playlistId': 'PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG', 'position': 0, 'resourceId': {'kind':
    # 'youtube#video', 'videoId': 'dAMo12gqYac'}, 'videoOwnerChannelTitle': 'AndreSuarezVEVO', 'videoOwnerChannelId':
    # 'UC7naKV_391fuue7aSZTvpaw'}}
    items = [
        dict(
            url=f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s',
            title=t["snippet"]["title"]
        ) for t in playlist_items
    ]
    return items


def download_audio(link):
    return YouTube(link).streams.get_audio_only().download(filename='song', output_path=AUDIO_DOWNLOAD_DIR, max_retries=5)


def insert_video_in_db(con, video_data):
    cur = con.cursor()
    try:
        cur.execute('''INSERT INTO VIDEOS(URL, TITLE, UPLOAD) VALUES('{0}', '{1}', FALSE);'''.format(video_data['url'], video_data['title']))
        print("Video correctly inserted: ", video_data['url'])
    except UniqueViolation:
        print("Video URL already exists: ", video_data['url'])
        pass
    con.commit()


def save_in_db_urls(con, list_videos_data):
    for video_data in list_videos_data:
        insert_video_in_db(con, video_data)


def create_database_connection():
    con = psycopg2.connect(
        database=db_credentials['NAME'],
        user=db_credentials['USER'],
        password=db_credentials['PASSWORD'],
        host=db_credentials['HOST'],
        port=db_credentials['PORT']
    )
    print("Database opened successfully")
    return con


def update_videos_url_from_playlist():
    con = create_database_connection()
    cur = con.cursor()
    # cur.execute('''DROP TABLE IF EXISTS VIDEOS;''')
    cur.execute('''CREATE TABLE IF NOT EXISTS VIDEOS
    (
        ID      SERIAL  PRIMARY KEY,
        URL     TEXT    NOT NULL    UNIQUE,
        TITLE   TEXT    NOT NULL,
        UPLOAD  BOOLEAN NOT NULL DEFAULT FALSE
    );''')
    con.commit()
    print("Table created successfully")
    save_in_db_urls(con, retrieve_videos_urls())
    con.close()


def download_random_song():
    con = create_database_connection()
    cur = con.cursor()
    cur.execute('''SELECT ID, URL, TITLE FROM VIDEOS WHERE UPLOAD IS FALSE''')
    result = cur.fetchall()
    cur.close()
    con.close()
    songs = [el for el in result]

    selected_song = None
    video_name = None
    while True:
        print(songs)
        random_song = choice(songs)
        print(random_song)
        try:
            download_audio(random_song[1])
            video_name = random_song[2]
        except PytubeError:
            continue
        else:
            selected_song = random_song[0]
            break

    if selected_song is not None:
        convert()
        upload_video(video_name)


def upload_video(video_name):
    print("Trying to upload video to FB page")
    pass


download_random_song()
# update_videos_url_from_playlist()
