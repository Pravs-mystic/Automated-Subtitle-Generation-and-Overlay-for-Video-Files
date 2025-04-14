# Automated-Subtitle-Generation-and-Overlay-for-Video-Files

## Project Description:

This Python-based project automates the end-to-end pipeline for generating and overlaying subtitles on video content. Leveraging state-of-the-art speech recognition (via Faster Whisper) and OpenCV-based video processing, the system performs the following core tasks:

## Video Format Standardization:

Converts input videos to .mp4 format using ffmpeg, ensuring compatibility for downstream processing.

## Audio Extraction:

Isolates the audio track from the video using ffmpeg-python, saving it as a WAV file for transcription.

## Speech-to-Text Transcription:

Utilizes the Faster Whisper ASR (Automatic Speech Recognition) model (small variant) to transcribe speech into segmented text with precise time alignment (start_time, end_time).

## Subtitles Rendering:

Overlays transcribed subtitles directly onto video frames using OpenCV.

## Allows full customization of subtitle appearance:

Font (e.g., HERSHEY_SIMPLEX, HERSHEY_COMPLEX)

Text color, background color, font size, thickness

(Optional) Placeholder for future text effects (e.g., animations or transitions)

## Audio-Video Recombination:

After subtitle rendering, the system recombines the original audio with the processed video using moviepy, preserving the original sound while embedding readable subtitles.

## Execution Mode:

Command-line interface (CLI) with customizable parameters for color, font, and styling.
