import os
import sys
import subprocess
import cv2
import numpy as np
from faster_whisper import WhisperModel
import soundfile as sf
import ffmpeg
import moviepy.editor as mp

def convert_video_to_mp4(input_file):
    output_file = input_file.rsplit('.', 1)[0] + '.mp4'
    subprocess.run(['ffmpeg', '-i', input_file, '-qscale', '0', output_file, '-loglevel', 'quiet'])
    return output_file

def extract_audio(input_video):
    extracted_audio = f"audio-{input_video.rsplit('.', 1)[0]}.wav"
    stream = ffmpeg.input(input_video)
    stream = ffmpeg.output(stream, extracted_audio)
    ffmpeg.run(stream, overwrite_output=True)
    return extracted_audio

def transcribe(audio):
    model = WhisperModel("small")
    segments, info = model.transcribe(audio)
    return segments

# Mapping of font names to OpenCV font constants
FONT_MAP = {
    "HERSHEY_SIMPLEX": cv2.FONT_HERSHEY_SIMPLEX,
    "HERSHEY_COMPLEX": cv2.FONT_HERSHEY_COMPLEX,
    "HERSHEY_TRIPLEX": cv2.FONT_HERSHEY_TRIPLEX,
    "HERSHEY_PLAIN": cv2.FONT_HERSHEY_PLAIN,
    "HERSHEY_SCRIPT_SIMPLEX": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
}

def overlay_subtitles_to_video(video_file, subtitles, output_file, text_color=(255, 255, 255), 
                                background_color=(0, 0, 0), font="HERSHEY_SIMPLEX", 
                                font_size=1, thickness=2, effect=None):
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_output_file = "temp_output.mp4"
    out = cv2.VideoWriter(temp_output_file, fourcc, fps, (width, height))

    # Get the OpenCV font constant from the font string
    font_face = FONT_MAP.get(font, cv2.FONT_HERSHEY_SIMPLEX)  # Default to HERSHEY_SIMPLEX if not found

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  # Convert to seconds
        for text, start_time, end_time in subtitles:
            if start_time <= current_time <= end_time:
                text_size = cv2.getTextSize(text, font_face, font_size, thickness)[0]
                text_x = (width - text_size[0]) // 2  # Center align text
                text_y = height - 50

                # Draw a filled rectangle behind the text for better visibility
                cv2.rectangle(frame, (text_x - 10, text_y - text_size[1] - 10), 
                                 (text_x + text_size[0] + 10, text_y + 10), background_color, -1)

                # Put the text on the frame
                cv2.putText(frame, text, (text_x, text_y), font_face, font_size, text_color, thickness, cv2.LINE_AA)

        out.write(frame)

    cap.release()
    out.release()

    # Check if the temporary video file was created and has content
    if os.path.getsize(temp_output_file) == 0:
        print("Error: Temporary video file is empty.")
        return

    # Combine video with audio
    video_clip = mp.VideoFileClip(temp_output_file)
    audio_clip = mp.AudioFileClip(video_file)  # Load the original audio

    # Check if video_clip duration is set
    if video_clip.duration is None:
        print("Error: Video clip duration is None.")
        return

    final_video = video_clip.set_audio(audio_clip)
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac')

    # Clean up temporary file
    video_clip.close()
    audio_clip.close()
    os.remove(temp_output_file) 

    # Clean up temporary files
    os.remove(video_file)  # Remove the original video file if needed
    # Assuming extracted_audio is defined somewhere in your code
    # os.remove(extracted_audio)  # Remove the extracted audio file if needed

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python subtitles.py <video_file> [<text_color> <background_color> <font> <font_size> <thickness> <effect>]")
        sys.exit(1)

    video_file = sys.argv[1]
    text_color = tuple(map(int, sys.argv[2].strip('()').split(','))) if len(sys.argv) > 2 else (255, 255, 255)  # Default white
    background_color = tuple(map(int, sys.argv[3].strip('()').split(','))) if len(sys.argv) > 3 else (0, 0, 0)  # Default black
    font = sys.argv[4] if len(sys.argv) > 4 else "HERSHEY_SIMPLEX"  # Default font
    font_size = float(sys.argv[5]) if len(sys.argv) > 5 else 1  # Default font size
    thickness = int(sys.argv[6]) if len(sys.argv) > 6 else 2  # Default thickness
    effect = sys.argv[7] if len(sys.argv) > 7 else None  # Default effect is None

    # Process the video
    # Check if the video file is in MP4 format
    if not video_file.lower().endswith('.mp4'):
        mp4_file = convert_video_to_mp4(video_file)
    else:
        mp4_file = video_file
    
    audio_file = extract_audio(mp4_file)
    segments = transcribe(audio_file)
    formatted_segments = [(segment.text, segment.start, segment.end) for segment in segments]
    overlay_subtitles_to_video(mp4_file, formatted_segments, "output_video.mp4", text_color, background_color, font, font_size, thickness, effect)

    # Clean up
    os.remove(audio_file) 