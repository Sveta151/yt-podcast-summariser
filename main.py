import os
from youtube_transcript_api import YouTubeTranscriptApi
import json
import requests

def get_video_id(url):
    # Extract video ID from YouTube URL
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "youtube.com" in url:
        return url.split("v=")[1].split("&")[0]
    else:
        raise ValueError("Invalid YouTube URL")

def get_transcript(video_id):
    print(video_id)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return None

def main():
    # Get YouTube video URL from user
    url = "https://youtu.be/v4T1oknATGU"
    
    # Extract video ID
    video_id = get_video_id(url)
    
    # Get transcript
    transcript = get_transcript(video_id)
    if transcript:
        # Save transcript to file
        with open('transcript.txt', 'w', encoding='utf-8') as f:
            f.write(transcript)
        print("Transcript has been saved to transcript.txt")


    if transcript:
        # Prepare the API request
        api_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3",
            "prompt": f"summarise and give key insights from {transcript}"
        }

        # Send the API request
        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            # Read the response line by line
            summary = ""
            for line in response.iter_lines():
                if line:
                    try:
                        json_line = json.loads(line)
                        summary += json_line.get('response', '')
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON: {line}")

            # Write the summary to a text file
            with open('summary.txt', 'w') as f:
                f.write(summary)

            print("Summary has been written to summary.txt")
        else:
            print(f"Error: Unable to get summary. Status code: {response.status_code}")
    else:
        print("No transcript available to summarize.")

if __name__ == "__main__":
    main()
