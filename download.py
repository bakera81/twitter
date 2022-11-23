from __future__ import unicode_literals

import json
import subprocess
import os
import requests
import re
import youtube_dl
# TODO: use gallery_dl directly
# import gallery_dl 

with open('twitter_secret.json', 'r') as f:
    creds = json.load(f)

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        # print(msg)
        pass

    def error(self, msg):
        print(msg)

def get_tweet_id(url):
    return url.split('/')[-1]

#TODO: confirm that both youtube-dl and gallery-dl work for private tweets
ydl_opts = {
    'user': creds.get('user'), 
    'password': creds.get('password'),
    'logger': MyLogger()
    # 'output': output_template
}

with open('like.js', 'r') as f:
    likes = json.load(f)

# TODO: Add a log with tweet IDs, paths, and logs (was image found, was video found, etc)
# TODO: to do this, we need to be able to understand if the download was successful
# TODO: Some tweets are quote tweets for deleted tweets, but are still valid (like 1536768228948598784)
# TODO: This tweet failed for some reason 1470737062735265797

n = len(likes)
# for i, like_obj in enumerate(likes):
# Left off: [3264/4258]
for i in range(3264, n):
    like = likes[i].get('like')
    # like = like_obj.get('like')
    tweet_id = get_tweet_id(like.get('expandedUrl'))
    url = like.get('expandedUrl')
    print("[{0}/{1}] Tweet ID: {2}".format(i, n, tweet_id))
    # print(like.get('fullText'))
    
    # Tweets missing fulltext have been deleted.
    if like.get('fullText') is None:
        print('Tweet has been deleted.')
    # TODO: some tweets link to articles or other webpages, not video/images
    elif 'https://' in like.get('fullText'): 

        # Parse URL from end of tweet
        # TODO: Some tweets have a URL that isn't at the end (like 748229992367144960)
        match = re.search("(?P<url>https?://t.co/[^\s]+$)", like.get('fullText'))

        if match:
            # Remove parentheses
            media_url = re.sub('\)', '', match.group("url"))
            resp = requests.head(media_url)

        # Only try to parse media if it is content from twitter
        # resp.status_code == 301
        if match is None or 'https://twitter.com/' not in resp.headers["Location"]:
            print('Link in tweet is not Twitter media.')
        else:
            # FETCH VIDEO

            # Create / change directory for youtube-dl
            # TODO: set a path without changing directory.
            video_dir = './youtube-dl/{}'.format(tweet_id)
            try:
                os.mkdir(video_dir)
            except OSError:
                pass
            
            os.chdir(video_dir)
            # Download video if possible
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try: 
                    # print("downloading video at {}...".format(url))
                    ydl.download([url])
                    # print("finished.")
                    # Change directory back
                    os.chdir('../..')
                except youtube_dl.DownloadError as e:
                    # For the love of god do this a better way
                    print('No video found. Removing directory '.format(video_dir))
                    os.chdir('../..')
                    os.rmdir(video_dir)
                    # print(e)

            # FETCH IMAGES

            gallery_dl = [
                'gallery-dl', 
                '-u', creds.get('user'), 
                '-p', creds.get('password'),
                url
                # '-d', 'resources'
            ]

            try: 
                # print("downloading images...")
                # subprocess.run(gallery_dl, shell=True, check=True)
                subprocess.run(gallery_dl, check=True)
                # print("finished.")
            except subprocess.SubprocessError as e: 
                print(e.output)
                pass

    else: 
        print('No additional media for tweet...')