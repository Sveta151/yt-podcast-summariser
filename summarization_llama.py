import ollama
transcript = """some example of transcript"""
channel_name = "some name"
name_of_the_video = "some name"

import textwrap


#if summary is too long llama3.1 strugling to generate short summary 
# that is why we need no chunk it , create separate summaries and then combine and create final summary
def chunk_transcript(transcript, chunk_size=10000):
    return textwrap.wrap(transcript, chunk_size)

def summarize_chunk(chunk, channel, name_of_the_video):
    input_text = f"""channel name: {channel}
    title of the video: {name_of_the_video}
    transcript of the video: {chunk}"""
    
    response = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'system',
            'content': """You are an agent that creates **very concise summaries** based on chunks of a transcript from a YouTube video. 
            Each summary should be strictly **7-10 sentences** and focus only on the main points from the chunk, helping users decide if the video matches their needs. 
            **Do not elaborate or provide unnecessary details**; keep the summary short and precise."""
        },
        {
            'role': 'user',
            'content': input_text
        }
    ])
    return response['message']['content'] 


# combining summaries
def generate_final_summary(chunk_summaries):
    combined_summary = " ".join(chunk_summaries)
    
    response = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'system',
            'content': """You are an agent that combines summaries into a concise final summary. 
            Provide a **concise summary** of 3-4 sentences  based on these summaries."""
        },
        {
            'role': 'user',
            'content': combined_summary
        }
    ])
    
    return response['message']['content']  



# generating key aspects separetly 
def generate_key_points(chunk_summaries):
    combined_summary = " ".join(chunk_summaries)
    
    response = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'system',
            'content': """You are an EdYoutubeHelper that based on the chunked summaries of the youtube video transcript  provide few **main** key aspects that can be learned from this video.
            It will help user to decide what he can learn from the video and is the aspect that he is looking for is covered in this video.
            Create them formated as the points. Provide just final keypoints. It should be very short points containing only 4-5 words per point."""
        },
        {
            'role': 'user',
            'content': combined_summary
        }
    ])
    
    return response['message']['content']


