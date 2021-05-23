from pytube import YouTube
from pytube.exceptions import PytubeError
import psycopg2
from psycopg2.errors import UniqueViolation
import os
from urllib import parse
from googleapiclient import discovery
from urllib.parse import parse_qs, urlparse
from random import choice


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
    items = [
        dict(
            url=f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s',
            title=t["snippet"]["title"]
        ) for t in playlist_items
    ]
    return items


def download_audio(link):
    return YouTube(link).streams.get_audio_only().download(filename='song', output_path=AUDIO_DOWNLOAD_DIR, max_retries=5)


# videos_urls = ['https://www.youtube.com/watch?v=dAMo12gqYac&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=9_xVpA6CETk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=KGzz2qOlxVQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=GuE8JgULP5s&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=lnXe37BB32I&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=_gm5piKnrS4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=rU-MMv13l-Q&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=7XPmRUp_Yf4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=VOcHCx2_oF4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=l4vZkdpfYdg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=cSUEFDZ3p3k&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=VTB5y4pFCCY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=R4NG_5XNa8U&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=HTxiZ4VvlPg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=uvEWuVrm1FU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Mcj75l2gJcY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QfhEKpFiepM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=2GhF2mPKnDg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=9ulUu1G6VZo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=PiT7OU2UemI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=GxQjx7FkmNA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=d5Qki0wGHr4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=X98HLdKgGmM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=k4DbYg1bgkc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=qkkG6g6vT34&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=7h2ryr_uUEs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=zpSBU0eUmmw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=6TK_KAIo4ZU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=luekHkWCaoo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=C8Vz1ZHgfJc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=7ZlFnlC72Qc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=NYi66-jxoyE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=7bAaa9fPgNo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=sHk-UtX5g_Q&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ktuPLFBcOOQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=K3eKVFC-VyU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Z2T4Kn24Sso&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=BtPKcz0XMIg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=eHWhbwWX7_g&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=8yEUKf2P4i0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=nhIfAdGYXq0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=sct0-7rs2zY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=yl_Oy6Uvr-w&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QINbgIJRPSQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Ht_sdb16LLQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=uQ98d5D3nC0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=3kYitK-KoWY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=AEfMc6mfgEk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=IAaGFLWQQjw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=K3eKVFC-VyU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=luekHkWCaoo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=I7Qi81-PjJg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=klNdNj3-xS8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=6EEYSbjkdlM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Xgxu08FF4YE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=PAbcbCDlMb8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=F_zeJu0TM4o&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=HguJjFpCCHM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=yUX73shxxPE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=6LAbDZOAn2o&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=OLrojSxHhmA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=GUb1Kdl5d8g&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Mw2cy_7rWF0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=0jgVoAdNioM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=7E4czIc4PW8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=gpJlFkCMV8A&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=sRvGLV75puw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=zvisX51IXZo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=lt95zgMhdtg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=_KQPR8lgxsU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=d9CPSBIwHb8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=KFy5Y_VGFjE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=x0n3JKL7Qkc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=lvfyf7R8NVg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=76NTqWYunms&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=_lupbUIY8eo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=hk-TTzavV3w&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=0dMmVvhIMHM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=I7Qi81-PjJg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=7LhqewIGe0w&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=XcaxfCnbZAA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=HuCD8u0hnfk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=WU_TdONsI5k&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=-cPjqWH5rJ4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Vj1190w58UM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=klNdNj3-xS8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=K3eKVFC-VyU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=zLX_GcXt2pI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Fw2FR43M4k0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=4d_UM_2UORo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=xIm16zAKsjs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=_GrQs-7TPfs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=wL1HMIMRoNY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=88hc0fcN6cM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=q808C7Lawmo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=IAaGFLWQQjw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=VVfKZgv9eSE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Geqmpq0tjNU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=npI4PIO5ij0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=wGZJRVcwZIY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=MP-0BPE6uxk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=huO6qzcIJ3g&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=bnS03AYIKp4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=oEz4uUvvb_4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=D9W4DLjmoOM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Q_bfKBC89OQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QsRhHEIn0Nw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=GuT6iKnQKBM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=jzvnFbsXxxA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=TK9_ElDYCYY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=5toRizDy648&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Geqmpq0tjNU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=BpyUAZ1ik1g&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=tKF2mF8BXUc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=_Idd7OWczEA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=wfift0DyExE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=AS5DOyyoXJI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=3nOMaejCYvA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=wGZJRVcwZIY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=eYegmKbyD6Y&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Iss0a4r1-ew&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=jucBuAzuZ0E&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=1g84OTR9F2Y&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=CktQxuDkYGg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=hKnfm_6yv38&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=7E4czIc4PW8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QINbgIJRPSQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=v0rmgtiH2Lc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=nB24dv2QGus&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=S_KpqCFORGc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=cNx4tK9sh2c&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=eVtNX3rG8SM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QwEeNuaRTUE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=R-3Y_urpXdc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=KPeFCmlRjZU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=pgo71qR8nN8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Js_6bXQ3REs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ijIfPabCBoI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=LASimTGySik&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=L8a8KN74D2s&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=vGYyVPZS3Wk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ovLbjuwXxH0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=o4KMJD3cRMc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=sct0-7rs2zY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=dnvVtkVaM84&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=0vICh9NuDE0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=1Nr_tqkMsJs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=219IlhVXHQg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=lmx_izr0CRY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=xTk-T4-E2to&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=2hvwvyQyab4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=HFOjUum13ts&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Iq01k8ygGyU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=m9EDaVMAcXg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=jVT06NQ-afg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=O_BmavloD10&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=im0dir_UwCs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=HL247-WWwuQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=pj4rOYws8Gw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=KOb0vNKfmSk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=nzDbDqfZMMY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=aq8CsZNTYzw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QZaUGf_z4KY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=PCeRWYvvPtg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=huCZ7dFwqgw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=IYj364cgamk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=94J9VrY9QBA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Dj1MRUkZu6s&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=uDNPbkZ4my4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=dA7xYuiNqIc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=h_Z_bupvoBg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QEIVmz5jTOY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=6r8mlDvfyZI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=D9W4DLjmoOM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=S4lZHCgefMI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=DV3zm1l-FpE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=OukQDrJ7QRQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=zLX_GcXt2pI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=AiyuVwv67n0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=fzm3wEARkaA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=BERCMdeS7uw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Y2hI2Wk9qKc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ShcpC8sBnjk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=pqJBXjzBr_U&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=OPauiOoaXsc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=sBtR4ou2PqQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ec9m3v_k3mE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=U-_ri--5070&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=W8a_LOgFCVs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=egxK3ArGtRM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=M6LuBqu2nVk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=hJBXaq5-64g&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=t3iHzMlTjQQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=iiD79HLck0U&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=P91Rcm6bruQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=t53inYwEJb8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=UC3lKuBeQL8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ljZ0vY0-Ve8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=G4SN4qMRE-U&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=wkX2Vaxgq_8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=InJODYmnvGo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=0qiG_LzTVBA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=t53inYwEJb8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=-ZokPrqyBRw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=nYngIrcr8_c&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Vnanybz-R3g&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=MavDpvV2yxc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=uTFQ0QgoL3M&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=zxyr8vrEB0Y&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=zqifVY1plq4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=0T6aUzIwa_E&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=GTrfrBuULAk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=1sTJGs63S8U&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ZpFuTf9Rf2w&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=hOjNS-2metw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Fe4l40BIG3Q&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=tGeNCO9N560&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=SBqxeoaj6GA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=bHAiEQlRR1U&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=3iWgF5VfUSU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=VvcFclB_yuc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=UtjgLOL6zxo&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=oV48YMsueqM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=WDl031ZDeI0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Iq01k8ygGyU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=SyVuCpF4OxY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=m9EDaVMAcXg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=7LhqewIGe0w&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=-RiwbE7eDNQ&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=R2rP8ZU52gU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=GtujUCURgtM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=LASimTGySik&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=S22afP9wODE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=6hD0p4qtPP4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=dWBt7qP1X-g&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=im0dir_UwCs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=sE_pGrPRoSk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=vADhBZElGgc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=O_BmavloD10&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=lNL1YrGIjk4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QKLIRbAbThU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=pqBbaQbEsj0&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=nojyDq8AKsE&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=MmNMNng6YJI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=dp1WvhZ_jLM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=4lSOlXgv6hc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=qJSySGuQVCI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=sqeAf-zFSxI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ygJg7htu5Co&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=UjsmsUwy_-c&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=8kkDH_AqW9k&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=DVo6CwjQlvw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=KCKwyG-HX7s&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=6cgzkS4hLYw&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=ZtG13teO-R8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=RL95LGfyhsU&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=g0wt4-yTrP4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=QuAncYDcZJk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Y5_McovG_xY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=tLax-xTwjas&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=lW6JfhepSVY&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=-VKGMhD5zUA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=hyXT11l6NFs&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=MXGcsAksjlc&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=RTtFeO6OEeg&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=FF1kCRmFR6M&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=Rhp79YyvTQA&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=MVQ_ZrcrFD4&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=IrR0-mIbBrI&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=pgo71qR8nN8&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=cmmJ1uiRiUM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=rVmiP7fF71A&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=9GDEicQlr5E&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=wtpIKU2IAyk&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s',
# 'https://www.youtube.com/watch?v=kb1c3QUwGGM&list=PLIYelo-VfHm8l5GXV0-exxU5jJ2Uf2acG&t=0s']


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


def download_shuffle_song():
    con = create_database_connection()
    cur = con.cursor()
    cur.execute('''SELECT ID, URL FROM VIDEOS WHERE UPLOAD IS FALSE''')
    result = cur.fetchall()
    cur.close()
    con.close()
    songs = [el for el in result]

    selected_song = None
    file_path_selected_song = None
    while True:
        print(songs)
        random_song = choice(songs)
        print(random_song)
        try:
            file_path_selected_song = download_audio(random_song[1])
        except PytubeError:
            continue
        else:
            selected_song = random_song[0]
            break

    if selected_song is not None:
        upload_song(file_path_selected_song)


def upload_song(file_path_song):
    print(file_path_song)
    print("Try to upload song")
    pass


# download_shuffle_song()
update_videos_url_from_playlist()


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
