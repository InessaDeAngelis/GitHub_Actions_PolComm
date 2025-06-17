#### Preamble ####
# Purpose: Get video info for selected MPs via GitHub Actions
# Author: Inessa De Angelis
# Date: 16 June 2025
# Contact: inessa.deangelis@mail.utoronto.ca
# License: MIT

#### Libraries set up ####
import requests
import csv
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

#### API KEY ####
key = os.getenv("API_KEY")

## Check if API key is present ##
if not key:
    print("API key is missing. Please check your .env file.")
    exit(1)

#### Set up CSV file to save all responses ####
csv_file = "YouTube/sample_video_info.csv"

#### Set up last run time file ####
last_run_file = "YouTube/last_run_time.txt"

#### Define function to get or initialize last run time ####
def get_last_run_time():
    if os.path.exists(last_run_file):
        with open(last_run_file, 'r') as file:
            last_run_time_str = file.read().strip()
            try:
                last_run_time = datetime.fromisoformat(last_run_time_str)
            except ValueError:
                last_run_time = datetime.now(pytz.utc)  # Default to now if there's an issue
    else:
        last_run_time = datetime.now(pytz.utc)  # Initialize to now if file does not exist
    return last_run_time

#### Define function to update last run time ####
def update_last_run_time(current_time):
    with open(last_run_file, 'w') as file:
        file.write(current_time.isoformat())

#### Create function to check if videos have comments ####
def check_video_comments(video_id):
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={key}"
        request = requests.get(url)
        request.raise_for_status()
        data = request.json()
        if "items" in data:
            comments = data["items"]
            return "Yes" if comments else "No"
        else:
            print(f"No 'items' key in response for video {video_id}. Response: {data}")
            return "Unknown"
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving comments for video {video_id}: {str(e)}")
        return "Unknown"
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Unknown"

## Get last run time ##
cutoff_date = get_last_run_time()
print(f"Filtering videos published after: {cutoff_date}")

## Open CSV file for writing with newline='' ##
with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Username', 'Title', 'Video_URL', 'Publish_Date', 'Has_Comments']
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    ## Write header row ##
    csvwriter.writeheader()

    ## Open file containing channel names ##
    with open('YouTube/politicians.txt', 'r') as file: 
        channel_names = file.readlines()

    ## Iterate through each channel name ##
    for channel in channel_names:
        channel = channel.strip()  

        try:
            ## Retrieve the channel id from the username ##
            url = f"https://youtube.googleapis.com/youtube/v3/channels?forUsername={channel}&key={key}"
            request = requests.get(url)
            data = request.json()
            if "items" in data and len(data["items"]) > 0:
                channelid = data["items"][0]["id"]
            else:
                raise ValueError(f"No channel found for username {channel}. Response: {data}")

        except Exception as e:
            ## Perform a channel search if channel id/username fails ##
            url = f"https://youtube.googleapis.com/youtube/v3/search?q={channel}&type=channel&key={key}"
            request = requests.get(url)
            data = request.json()
            if "items" in data and len(data["items"]) > 0:
                channelid = data["items"][0]["id"]["channelId"]
            else:
                print(f"No channel found for search query {channel}. Response: {data}")
                continue

        ## Create playlist id ##
        playlistid = list(channelid)
        playlistid[1] = "U"
        playlistid = "".join(playlistid)

        ## Query the uploads playlist and write to CSV ##
        nextPageToken = ""
        while True:
            videosUrl = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&playlistId={playlistid}&pageToken={nextPageToken}&maxResults=50&fields=items(contentDetails(videoId,videoPublishedAt),snippet(publishedAt,title)),nextPageToken&key={key}"
            response = requests.get(videosUrl)
            data = response.json()

            if "items" in data:
                for video in data["items"]:
                    video_title = video["snippet"]["title"]
                    publish_date_str = video["snippet"]["publishedAt"]
                    publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))
                    
                    if publish_date > cutoff_date:
                        video_id = video["contentDetails"]["videoId"]
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        has_comments = check_video_comments(video_id)
                        username = channel.strip()  

                        ## Write data to CSV file ##
                        csvwriter.writerow({
                            'Username': username, 
                            'Title': video_title, 
                            'Video_URL': video_url, 
                            'Publish_Date': publish_date_str, 
                            'Has_Comments': has_comments
                        })
            else:
                print(f"No 'items' key in videos response for playlist {playlistid}. Response: {data}")
                break

            ## Move to the next page ##
            nextPageToken = data.get("nextPageToken", None)
            if not nextPageToken:
                break

## Update last run time ##
update_last_run_time(datetime.now(pytz.utc))

print(f"CSV file '{csv_file}' has been created successfully.")
