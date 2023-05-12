import os
from pathlib import Path

from moviepy.editor import *
from pydub import AudioSegment
from pytube import YouTube


def download_audio(youtube_url, download_dir: Path):  
    # Create a YouTube object and download the video
    yt = YouTube(youtube_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    print(yt.title)
    audio_stream.download(output_path=download_dir)

def get_audio_object(source_webm_file: Path):    
    return AudioSegment.from_file(source_webm_file)

def extract_segments(audio_file, start_audio_part, end_audio_part,filename,output_data_dir: Path):     
    # get audio part from the original file
    start_audio_part = start_audio_part*1000
    end_audio_part = end_audio_part*1000        
    audio_segment = audio_file[start_audio_part: end_audio_part]
    print(audio_segment)
    # set filenames   
    output_data_path = f"{output_data_dir}/{filename}_{start_audio_part}_{end_audio_part}.wav"
    # save audio
    audio_segment.export(output_data_path, format="wav")    

if __name__ == '__main__':
    import argparse

    # video url
    # url = ''    
    # download_dir = '/home/yen/hackathon/parliamentary_sessions_dataset/downloads/'
    # download_audio(url, download_dir)

    parser = argparse.ArgumentParser(description="""\
    Extract each segment as its own wav into the new data directory.
    python3 slicung.py -o slicing_audio -w ./downloads/130571196.webm 
    """, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-w', '--source-webm-file', type=Path)
    parser.add_argument('-o', '--output-data-dir', type=Path)
    parser.add_argument('-start', '--start-segment', type=int)
    parser.add_argument('-end', '--end-segment', type=int)

    args = parser.parse_args()

    # get audio object
    audio_file = get_audio_object(args.source_webm_file)    
    filename = "_".join(os.path.splitext(os.path.basename(args.source_webm_file))[0].split())
    extract_segments(audio_file, args.start_segment, args.end_segment,
                    filename, args.output_data_dir)
