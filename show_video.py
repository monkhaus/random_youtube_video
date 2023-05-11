import sqlite3
import random

# Connect to the SQLite database
conn = sqlite3.connect('mydatabase.db')

# Retrieve a list of all video records
cursor = conn.execute('''SELECT channel_url, youtube_video_id FROM videos''')
video_records = cursor.fetchall()

# Choose a random video record from the list
random_record = random.choice(video_records)

# Print the channel url and youtube video id of the random record
channel_url, video_id = random_record
print(f"Channel URL: {channel_url}")
print(f"https://www.youtube.com/watch?v={video_id}")

# Close the connection to the database
conn.close()