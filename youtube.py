from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import mysql.connector
import datetime
import streamlit as st

def Api_connect():
    Api_Id="AIzaSyCQ49rcn02aPPs3H26x9kZUxyBI-xDlz2M"

    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name,api_version,developerKey=Api_Id)
    return youtube

youtube=Api_connect()

channel_name = 'Microsoft'
channel_response = youtube.channels().list(
    part='snippet,statistics',
    forUsername=channel_name  # Use channel name instead of the IDs
).execute()

if 'items' in channel_response:
    channel_data = channel_response['items'][0]
    channel_id = channel_data['id']
    channel_name = channel_data['snippet']['title']
    channel_type = channel_data['snippet']['description']  # Fix the description retrieval
    channel_views = channel_data['statistics']['viewCount']
    channel_description = channel_data['snippet']['description']
    subscriber_count = channel_data['statistics']['subscriberCount']
    total_video_count = channel_data['statistics']['videoCount']

    print(f"Channel Name: {channel_name}")
    print(f"Channel ID: {channel_id}")
    print(f"Channel Type: {channel_type}")
    print(f"Channel Views: {channel_views}")
    print(f"Channel_Description: {channel_description}")
    print(f"Subscribers: {subscriber_count}")
    print(f"Total Videos: {total_video_count}")

    # Retrieve playlists for the channel
    playlists_response = youtube.playlists().list(
        part='snippet',
        channelId=channel_id,
        maxResults=20  # You can adjust this, if you want more playlists
    ).execute()

    # Check if the response contains items
    if 'items' in playlists_response:
        # Extract playlist IDs
        playlist_ids = [item['id'] for item in playlists_response['items']]

        # Retrieve videos from each playlist
        for playlist_id in playlist_ids:
            playlist_response = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=20  # You can adjust this value to get more videos if needed
            ).execute()

            # Check if the response contains items
            if 'items' in playlist_response:
                video_ids = [item['contentDetails']['videoId'] for item in playlist_response['items']]
                print('Playlist_name')

                # Retrieve video information for each video
                for video_id in video_ids:
                    video_response = youtube.videos().list(
                        part='snippet,statistics',
                        id=video_id
                    ).execute()

                    # Check if the response contains items and is not empty
                    if 'items' in video_response and len(video_response['items']) > 0:
                        video_data = video_response['items'][0]
                        video_title = video_data['snippet']['title']
                        video_description = video_data['snippet']['description']
                        published_date = video_data['snippet']['publishedAt']
                        view_count = video_data['statistics'].get('viewCount', 'N/A')
                        like_count = video_data['statistics'].get('likeCount', 'N/A')
                        dislike_count = video_data['statistics'].get('dislikeCount', 'N/A')
                        favorite_count = video_data['statistics'].get('favoriteCount', 'N/A')
                        comment_count = video_data['statistics'].get('commentCount', 'N/A')
                        duration= video_data['statistics'].get('duration','N/A')
                        thumbnail_url = video_data['snippet']['thumbnails']['default']['url']

                        print(f"Video Title: {video_title}")
                        print(f"Video ID: {video_id}")
                        print(f"video_description: {video_description}")
                        print(f"view_count:{view_count}")
                        print(f"published_date:{published_date}")
                        print(f"Likes: {like_count}")
                        print(f"Dislikes: {dislike_count}")
                        print(f"favorite_count: {favorite_count}")
                        print(f"Comments: {comment_count}")
                        print(f"duration: {duration}")
                        print(f"thumbnail_url: {thumbnail_url}")
                        print()
                    else:
                        print(f"Video with ID {video_id} not found or has no statistics data.")

client = pymongo.MongoClient('mongodb+srv://phoorneshmurali:phoorneshih@cluster0.2r8dnjv.mongodb.net/?retryWrites=true&w=majority')
db = client["Youtube_data"]

def insert_channel_data(channel_data):
    channels_collection = db['channels']
    channels_collection.insert_one(channel_data)

def insert_playlist_data(playlist_data):
    playlists_collection = db['playlists']
    playlists_collection.insert_many(playlist_data)

def insert_video_data(video_data):
    videos_collection = db['videos']
    videos_collection.insert_many(video_data)

channel_data_to_insert = {
    'channel_id': channel_id,
    'channel_name': channel_name,
    'channel_type': channel_type,
    'channel_views': channel_views,
    'channel_description': channel_description,
    'subscriber_count': subscriber_count,
    'total_video_count': total_video_count
}
insert_channel_data(channel_data_to_insert)

playlist_data_to_insert = []
for playlist_id in playlist_ids:
    # Fetch playlist details from the YouTube API
    playlist_response = youtube.playlists().list(
        part='snippet',
        id=playlist_id
    ).execute()

    if 'items' in playlist_response and playlist_response['items']:
        playlist_name = playlist_response['items'][0]['snippet']['title']
        playlist_data_to_insert.append({
            'playlist_id': playlist_id,
            'channel_id': channel_id,
            'playlist_name': playlist_name
        })
    else:
        print(f"Playlist with ID {playlist_id} not found.")

insert_playlist_data(playlist_data_to_insert)

video_data_to_insert = []
for playlist_id in playlist_ids:
    playlist_response = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=20
    ).execute()

    if 'items' in playlist_response:
        video_ids = [item['contentDetails']['videoId'] for item in playlist_response['items']]

        for video_id in video_ids:
            video_response = youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()

            if 'items' in video_response and video_response['items']:
                video_data = video_response['items'][0]
                video_name = video_data['snippet']['title']
                video_description = video_data['snippet']['description']
                published_date = video_data['snippet']['publishedAt']
                view_count = video_data['statistics'].get('viewCount', 'N/A')
                like_count = video_data['statistics'].get('likeCount', 'N/A')
                dislike_count = video_data['statistics'].get('dislikeCount', 'N/A')
                favorite_count = video_data['statistics'].get('favoriteCount', 'N/A')
                comment_count = video_data['statistics'].get('commentCount', 'N/A')
                duration = video_data['statistics'].get('duration', 'N/A')
                thumbnail_url = video_data['snippet']['thumbnails']['default']['url']

                video_data_to_insert.append({
                    'video_id': video_id,
                    'playlist_id': playlist_id,
                    'video_name': video_name,
                    'video_description': video_description,
                    'published_date': published_date,
                    'view_count': view_count,
                    'like_count': like_count,
                    'favorite_count': favorite_count,
                    'comment_count': comment_count,
                    'duration':duration,
                    'thumbnail_url':thumbnail_url
                    # Add other fields here as needed
                })
            else:
                print(f"Video with ID {video_id} not found or has no statistics data.")

insert_video_data(video_data_to_insert)

client.close()

def convert_iso8601_to_mysql(iso_datetime_str):
    try:
        iso_datetime = datetime.datetime.strptime(iso_datetime_str, "%Y-%m-%dT%H:%M:%SZ")
        return iso_datetime.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(f"Error converting datetime: {e}")
        return None
    
def handle_non_integer(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None 
    
mongo_client = pymongo.MongoClient('mongodb+srv://phoorneshmurali:phoorneshih@cluster0.2r8dnjv.mongodb.net/?retryWrites=true&w=majority')
mongo_db = mongo_client['Youtube_data']
mongo_channels_collection = mongo_db['channels']
mongo_playlists_collection = mongo_db['playlists']
mongo_videos_collection = mongo_db['videos']

mysql_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    port='3306',
    password='password',
    database='youtube' )
mysql_cursor = mysql_connection.cursor()

mysql_cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        channel_id VARCHAR(500),
        channel_name VARCHAR(500),
        channel_type TEXT,
        channel_views BIGINT,
        channel_description TEXT,
        subscriber_count INT,
        total_video_count INT
        
    )
''')
#to insert playlist details

mysql_cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
        playlist_id VARCHAR(500),
        channel_id VARCHAR(500),
        playlist_name VARCHAR(500)
        
    )
''')
#to insert video details
mysql_cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        video_id VARCHAR(500),
        playlist_id VARCHAR(500),
        video_name VARCHAR(500),
        video_description TEXT,
        published_date DATETIME,
        view_count BIGINT,
        like_count INT,
        dislike_count INT,
        favourite_count INT,
        comment_count INT,
        duration INT,
        thumbnail_url TEXT
        
    )
''')

mysql_connection.commit()

try:
    # Insert channel data from MongoDB into MySQL
    channel_data = mongo_channels_collection.find()
    for channel in channel_data:
        channel_id = channel.get('channel_id', None)
        channel_name = channel.get('channel_name', None)
        channel_type = channel.get('channel_type', None)
        channel_views = handle_non_integer(channel.get('channel_views', None))
        channel_description = channel.get('channel_description', None)
        subscriber_count = channel.get('subscriber_count', None)
        total_video_count = channel.get('total_video_count', None)

        if channel_id is not None:
            insert_query = '''
                INSERT INTO channels (channel_id, channel_name, channel_type, channel_views, channel_description, subscriber_count, total_video_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            mysql_cursor.execute(insert_query, (channel_id, channel_name, channel_type, channel_views, channel_description, subscriber_count, total_video_count))

    # Insert playlist data from MongoDB into MySQL
    playlist_data = mongo_playlists_collection.find()
    for playlist in playlist_data:
        playlist_id = playlist.get('playlist_id', None)
        channel_id = playlist.get('channel_id', None)
        playlist_name = playlist.get('playlist_name', None)
        if playlist_id is not None:
            insert_query = '''
                INSERT INTO playlists (playlist_id, channel_id, playlist_name)
                VALUES (%s, %s, %s)
            '''
            mysql_cursor.execute(insert_query, (playlist_id, channel_id, playlist_name))

    # Insert video data from MongoDB into MySQL
    video_data = mongo_videos_collection.find()
    for video in video_data:
        video_id = video.get('video_id', None)
        playlist_id = video.get('playlist_id', None)
        video_name = video.get('video_name', None)
        video_description = video.get('video_description', None)
        published_date_iso8601 = video.get('published_date', None)
        view_count = handle_non_integer(video.get('view_count', None))
        like_count = handle_non_integer(video.get('like_count', None))
        dislike_count = handle_non_integer(video.get('dislike_count', None))
        favourite_count = handle_non_integer(video.get('favourite_count', None))
        comment_count = handle_non_integer(video.get('comment_count', None))
        duration = handle_non_integer(video.get('duration', None))
        thumbnail_url = video.get('thumbnail_url', None)

        if video_id is not None:
            # Converting ISO 8601 datetime to MySQL datetime format
            published_date_mysql = convert_iso8601_to_mysql(published_date_iso8601)

            insert_query = '''
                INSERT INTO videos (video_id, playlist_id, video_name, video_description, published_date, view_count, like_count, dislike_count, favourite_count, comment_count, duration, thumbnail_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            mysql_cursor.execute(insert_query, (video_id, playlist_id, video_name, video_description, published_date_mysql, view_count, like_count, dislike_count, favourite_count, comment_count, duration, thumbnail_url))

    # Commit changes and close MySQL cursor and connection
    mysql_connection.commit()

except Exception as e:
    # Handle exceptions here (e.g., log the error, roll back the transaction)
    print(f"Error: {str(e)}")
    mysql_connection.rollback()

    # Commit changes and close MySQL cursor and connection
    mysql_connection.commit()


def connect_to_mysql():
    db_connection = mysql.connector.connect(
        host='localhost',
        user='root',
        port='3306',
        password='password',
        database='youtube'
    )
def execute_query(query):
    try:
        # Connect to MySQL
        with mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='youtube'
        ) as db_connection:
            # Create a cursor
            with db_connection.cursor() as cursor:
                # Execute the query
                cursor.execute(query)

                # Fetch all the results
                result = cursor.fetchall()

                # Create a DataFrame
                columns = [desc[0] for desc in cursor.description]
                result_df = pd.DataFrame(result, columns=columns)

        return result_df

    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    st.title("YouTube Data Analysis")

    # Query buttons
    query1_button = st.button("Query 1: Names of Videos and Their Corresponding Channels")
    query2_button = st.button("Query 2: Channels with Most Videos")
    query3_button = st.button("Query 3: Top 10 Most Viewed Videos")
    query4_button = st.button("Query 4: Comments on Videos")
    query5_button = st.button("Query 5: Videos with Most Likes")
    query6_button = st.button("Query 6: Total Likes and Dislikes for Videos")
    query7_button = st.button("Query 7: Total Views for Channels")
    query8_button = st.button("Query 8: Channels Publishing in 2022")
    query9_button = st.button("Query 9: Average Video Duration by Channel")
    query10_button = st.button("Query 10: Videos with Most Comments")

    if query1_button:
        query1 = """
        SELECT video_name, channel_name FROM combined_data;
        """
        result1 = execute_query(query1)
        st.header("Query 1: Names of Videos and Their Corresponding Channels")
        st.dataframe(result1)

    if query2_button:
        query2 = """
        SELECT channel_name, MAX(total_video_count) AS max_video_count
        FROM channels
        GROUP BY channel_name
        ORDER BY max_video_count DESC;
        """
        result2 = execute_query(query2)
        st.header("Query 2: Channels with Most Videos")
        st.dataframe(result2)

    if query3_button:
        query3 = """
        SELECT channel_name, video_name, MAX(view_count) AS max_view_count
        FROM combined_data
        GROUP BY channel_name, video_name
        ORDER BY max_view_count DESC
        LIMIT 10;
        """
        result3 = execute_query(query3)
        st.header("Query 3: Top 10 Most Viewed Videos")
        st.dataframe(result3)

    if query4_button:
        query4 = """
        SELECT video_name, like_count, dislike_count FROM combined_data;
        """
        result4 = execute_query(query4)
        st.header("Query 4: Comments on Videos")
        st.dataframe(result4)

    if query5_button:
        query5 = """
        SELECT channel_name, video_name, MAX(like_count) AS max_like_count
        FROM combined_data
        GROUP BY channel_name, video_name
        ORDER BY max_like_count DESC;
        """
        result5 = execute_query(query5)
        st.header("Query 5: Videos with Most Likes")
        st.dataframe(result5)

    if query6_button:
        query6 = """
        SELECT video_name, SUM(like_count) AS total_likes, SUM(dislike_count) AS total_dislikes
        FROM combined_data
        GROUP BY video_name;
        """
        result6 = execute_query(query6)
        st.header("Query 6: Total Likes and Dislikes for Videos")
        st.dataframe(result6)

    if query7_button:
        query7 = """
        SELECT channel_name, SUM(channel_views) AS total_views
        FROM channels
        GROUP BY channel_name;
        """
        result7 = execute_query(query7)
        st.header("Query 7: Total Views for Channels")
        st.dataframe(result7)

    if query8_button:
        query8 = """
        SELECT DISTINCT channel_name
        FROM combined_data
        WHERE YEAR(published_date) = 2022;
        """
        result8 = execute_query(query8)
        st.header("Query 8: Channels Publishing in 2022")
        st.dataframe(result8)

    if query9_button:
        query9 = """
        SELECT channel_name, AVG(duration) AS avg_duration
        FROM combined_data
        GROUP BY channel_name;
        """
        result9 = execute_query(query9)
        st.header("Query 9: Average Video Duration by Channel")
        st.dataframe(result9)

    if query10_button:
        query10 = """
        SELECT channel_name, video_name, MAX(comment_count) AS max_comment_count
        FROM combined_data
        GROUP BY channel_name, video_name
        ORDER BY max_comment_count DESC;
        """
        result10 = execute_query(query10)
        st.header("Query 10: Videos with Most Comments")
        st.dataframe(result10)

if __name__ == "__main__":
    main()


