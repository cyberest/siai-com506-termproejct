# Helper functions
# ===================

import time
import random

import requests

import os
import shutil
import hashlib
import re

# Wait for some random time to avoid IP ban
# Official Reddit API allows 60 calls per minute
# https://github.com/reddit-archive/reddit/wiki/API#rules
def rand_sleep(sec=0):
    time.sleep(sec * (random.random()+1))

# Store images into filesystem instead of database
def save_image(url, image_dir):
    IMAGE_DIR = image_dir
    rand_sleep()

    # restart Tor to get new proxy
    os.system('killall tor > /dev/null')
    os.system('service tor start > /dev/null')

    session = requests.session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    resp = session.get(url, stream=True)

    # Extract filename from full url
    file_name = re.search('[^/\\&\?]+\.\w{3,4}(?=([\?&].*$|$))', url).group()
    save_path = IMAGE_DIR + file_name
    with open(save_path, 'wb') as f:
        resp.raw.decode_content=True # force to decompress GZIP or deflate
        shutil.copyfileobj(resp.raw, f) # stream data to file object
    # Rename file as MD5 hash
    new_path = IMAGE_DIR + hash_file(save_path) + '.' + file_name.split('.')[1]
    os.rename(save_path, new_path)
    return new_path

# Hash file to get unique identifier to be stored in DB
def hash_file(file_path):
    BUFFER_SIZE = 65536  # read stuff in 64kb chunks
    md5 = hashlib.md5()

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


if __name__ == '__main__':
    pass