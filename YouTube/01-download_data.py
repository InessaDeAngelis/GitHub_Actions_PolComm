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
key = os.getenv("YOUTUBE_API_KEY")

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
                # Make sure the last run time is timezone-aware (UTC)
                last_run_time = datetime.fromisoformat(last_run_time_str).astimezone(pytz.utc)
            except ValueError:
                # Default to now (UTC) if there's an issue
                last_run_time = datetime.now(pytz.utc)
    else:
        # Initialize to now (UTC) if file does not exist
        last_run_time = datetime.now(pytz.utc)
    return last_run_time

#### Main loop where the comparison happens ####
for video in data["items"]:
    video_title = video["snippet"]["title"]
    publish_date_str = video["snippet"]["publishedAt"]
    # Make sure publish_date is timezone-aware (UTC)
    publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00'))  # Convert to UTC-aware datetime
    
    # Now both cutoff_date and publish_date are timezone-aware (UTC)
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
