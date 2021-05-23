import os
import requests
import json
import datetime


FB_ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
FB_PAGE_ID = os.getenv('FB_PAGE_ID')


def upload_video(title):
    print("Start upload video: ", datetime.datetime.now())
    fburl = 'https://graph-video.facebook.com/v10.0/{0}/videos?access_token={1}'.format(
        str(FB_PAGE_ID), str(FB_ACCESS_TOKEN)
    )
    data = {'description': title}

    files = {'file': open('converted.mp4', 'rb')}
    response = requests.post(fburl, data=data, files=files)
    print("End upload video: ", datetime.datetime.now())
    print(response)
    json_response = json.loads(response.text)
    print(json_response)
    return response.ok, json_response['id']
