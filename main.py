import os
from youtube_transcript_api import YouTubeTranscriptApi
import json
import requests
from sqlite import createdb,insert_summary,show_records,fetch_summary
import ollama
from rag import create_embedddb, search_top_matches, process_transcript

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
        
        def format_segment(start, end, text):
            return f"{start:.2f} - {end:.2f}: {text.strip()}"
        
        formatted_transcript = []
        current_chunk = ""
        chunk_start = 0
        
        for entry in transcript:
            while entry['start'] >= chunk_start + 30:
                if current_chunk:
                    formatted_transcript.append(format_segment(chunk_start, chunk_start + 30, current_chunk))
                    current_chunk = ""
                chunk_start += 30
            
            current_chunk += " " + entry['text']
        
        # Add the last chunk if there's any text left
        if current_chunk:
            formatted_transcript.append(format_segment(chunk_start, chunk_start + 30, current_chunk))
        
        return "\n".join(formatted_transcript)
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return None
    
def conversation(url):
    print("Do you want to have a conversation with the AI? (y/n)")
    user_input = input()
    if user_input.lower() == 'y':
        while True:
            print("Enter your message: (type exit to break)")
            message = input()
            if message.lower() == 'exit':
                break
            
            top_search_response = search_top_matches(message,url)
            print("top search found")
            # print(len(top_search_response))

            for match in top_search_response:
                print(f"Chunk: {match[0]}, Similarity: {match[1]}")


            # Concatenate the top search responses into a single string
            top_search_response_string = "\n".join([f"Chunk: {match[0]}, Similarity: {match[1]}" for match in top_search_response])

            # Create the final prompt
            initial_system_prompt = "Based on the information provide to you after doing a RAG search,answer user query based only on the context provide. if you don't know , just reply back Dont know the answer.\n\n"
            final_system_prompt = initial_system_prompt + top_search_response_string

            response = ollama.chat(model='llama3.1', messages=[
            {
                'role': 'system',
                'content': final_system_prompt
            },
            {
                'role': 'user',
                'content': message
            }
            ])
            generated_response = response['message']['content']
            print("AI Response:")
            print(generated_response)
    else:
        print("Conversation ended")

def process_youtube_video():
    # Get YouTube video URL from user
    # url = "https://youtu.be/v4T1oknATGU"

    url = input("Enter the YouTube video URL: ")
#check if summary present for the video url. If present then print the summary else then do the rest of the flow
    summary = fetch_summary(url)
    if summary:
        print("Summary already exists in the database:")
        print(summary)
        conversation(url)
        return
    
    # Extract video ID
    video_id = get_video_id(url)

    
    # Get transcript
    transcript = get_transcript(video_id)
    if transcript:
        # Save transcript to file
        with open('transcript.txt', 'w', encoding='utf-8') as f:
            f.write(transcript)
        print("Transcript has been saved to transcript.txt")

    process_transcript(url, transcript)
    generate_summary(url, transcript)
    
    conversation(url)


def generate_summary(url, transcript):
    if transcript:
        print("Generating summary...")

        try:
            response = ollama.chat(model='llama3.1', messages=[
            {
                'role': 'system',
                'content': 'summarise and give key insights for the transcript that user provides'
            },
            {
                'role': 'user',
                'content': transcript
            }
            ])
            summary = response['message']['content']
            print(summary)

            # Write the summary to a text file
            with open('summary.txt', 'w') as f:
                f.write(summary)

            print("Summary has been written to summary.txt")
            insert_summary(url, summary)
            print(summary)
            print("record inserted in db \n")
            # show_records()

        except ollama.ResponseError as e:
            print(f"Error: {e}")
            if e.status_code == 404:
                print("Model not found")
    else:
        print("No transcript available to summarize.")

def main():
    # fetch user input from user until he exits

    createdb()
    create_embedddb()
    while True:
        process_youtube_video()
        print("Do you want to continue? (y/n)")
        user_input = input()
        if user_input.lower() != 'y':
            break

    # mainflow()
        # print("Do you want to continue? (y/n)")
        # user_input = input()
        # if user_input.lower() != 'y':
            # break

if __name__ == "__main__":
    main()
