# DeepFrame Studio

Welcome to our Django web app for video processing! This application provides a variety of features for manipulating and enhancing your video content. The main emphasis is on two powerful AI features: DF (DeepFake) detection using a fine-tuned MesoNet and video colorization via DeOldify.

## Table of Contents
- [Features](#features)
- [Installation and Setup](#InstallationandSetup)
- [Usage](#Usage)
- [Dependencies](#Dependencies)
- [Contributing](#Contributing)

## Features

### Video Processing
1. **Video to Audio:** Convert videos to audio effortlessly.
2. **Change video format:** Change videos format effortlessly.
3. **Extract Frames from Video:** Capture still frames from your videos.
4. **Add Video to Audio:** Merge video content with different audio tracks.
5. **Reverse Video:** Play your videos backward for a unique perspective.
6. **Change Video Speed:** Adjust video playback speed to suit your preferences.
7. **Video Trimming:** Trim your videos to the desired length.
8. **Add Subtitles to Videos:** Enhance your videos by adding subtitles.
9. **Merge Multiple Videos:** Combine multiple videos into a single file.

### AI Features
10. **DF Detection using MesoNet:** Detect dense fog in videos using a fine-tuned MesoNet model.
11. **Video Colorization via DeOldify:** Apply advanced video colorization using the DeOldify model.

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Humzafazal72/DeepFrame-Studio.git
   cd DeepFrame Studio

2. Download and install ffmpeg (You can follow <a href="https://phoenixnap.com/kb/ffmpeg-windows">this tutorial</a>).
    
3. Import my Anaconda Virtual Environment 'environment.yml' (You can follow <a href="https://docs.anaconda.com/free/navigator/tutorials/manage-environments/">this tutorial</a>).

4. Install fastai:

   ```bash
   pip install fastai
      
5. Downloads the weights for DeOldify from <a href="https://data.deepai.org/deoldify/ColorizeVideo_gen.pth">this link</a>:

6. Place the .pth weights in the folder 'models' along with mesonet's weights.

7. Run the project using the command:

    ```bash
   python manage.py runserver
    
## Usage

Before any commercial use take permission from the owners of Deoldify and the creaters of CelebDFv2 dataset. 

## Dependencies

- Python 3.11.5
- Anaconda
- ffmpeg

## Contributing

- <a href="https://github.com/MaheenShahzad"> Maheen Shahzad </a>

