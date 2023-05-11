import re
import json
import requests
from bs4 import BeautifulSoup
import scrapetube
import sqlite3

url = 'https://www.youtube.com/channel/UCNajC7dxZrjTw4lBWWJYZ8w'


# Get the page source using requests and parse it using BeautifulSoup
soup = BeautifulSoup(requests.get(url, cookies={'CONSENT': 'YES+1'}).text, "html.parser")

# Extract the JSON data from the page source using regex
data = re.search(r"var ytInitialData = ({.*});", str(soup.prettify())).group(1)

# Parse the JSON data
json_data = json.loads(data)

# Extract channel information from the parsed JSON data
channel_id = json_data['header']['c4TabbedHeaderRenderer']['channelId']
channel_title = json_data['header']['c4TabbedHeaderRenderer']['title']
channel_logo = json_data['header']['c4TabbedHeaderRenderer']['avatar']['thumbnails'][2]['url']
channel_subscribers = json_data['header']['c4TabbedHeaderRenderer']['subscriberCountText']['simpleText'].strip(" subscribers").lower()

# Convert the subscriber count to an integer
if 'm' in channel_subscribers:
    channel_subscribers = int(float(channel_subscribers.strip('m')) * 1000000)
elif 'k' in channel_subscribers:
    channel_subscribers = int(float(channel_subscribers.strip('k')) * 1000)
else:
    channel_subscribers = int(channel_subscribers)
 
# Scrape the videos using scrapetube
videos = list(scrapetube.get_channel(channel_id))

# Create a list of video objects
video_objects = []
for video in videos:
    try:
        video_obj = {
            'channel_url': url,
            'youtube_video_id': video['videoId'],
            'title': video['title']['runs'][0]['text'],
            'thumbnail_url': video['thumbnail']['thumbnails'][3]['url'],
            'view_count': int(video['viewCountText']['simpleText'].replace(',', '').replace('views', '').strip())
        }
        video_objects.append(video_obj)
    except:
        pass

if video_objects:
    # Connect to the SQLite database
    conn = sqlite3.connect('mydatabase.db')

    # Create a table to store the videos
    conn.execute('''CREATE TABLE IF NOT EXISTS videos
                (channel_url TEXT,
                youtube_video_id TEXT,
                title TEXT,
                thumbnail_url TEXT,
                view_count INTEGER);''')

    # Insert the video objects into the table
    for video_obj in video_objects:
        conn.execute('''INSERT INTO videos (channel_url, youtube_video_id, title, thumbnail_url, view_count)
                    VALUES (?, ?, ?, ?, ?)''',
                    (video_obj['channel_url'], video_obj['youtube_video_id'], video_obj['title'],
                    video_obj['thumbnail_url'], video_obj['view_count']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
