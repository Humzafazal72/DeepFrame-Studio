# Your Django Video Processing Web App

Welcome to your Django web app for video processing! This application provides a variety of features for manipulating and enhancing your video content. The main emphasis is on two powerful AI features: DF (Dense Fog) detection using a fine-tuned MesoNet and video colorization via DeOldify.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Contributing](#contributing)

## Features

### Video Processing
1. **Video to Audio:** Convert videos to audio effortlessly.
2. **Video to Audio:** Change videos format effortlessly.
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

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Humzafazal72/DeepFrame-Studio.git
   cd DeepFrame Studio
   
2. Create a anaconda virtual environment with python version 3.11.5:
   
   ```bash
   conda create --name myenv python=3.11.5

3. Install all the dependencies from requirements.txt:
    ```bash
   pip install -r requirements.txt

4. Downloads the weights for DeOldify from <a href="https://data.deepai.org/deoldify/ColorizeVideo_gen.pth">this link</a>:

5. Place the .pth weights in the folder 'models' along with mesonet's weights.

7. Run the project using the command:

    ```bash
   python manage.py runserver
    
##Usage

Before any commercial use take permission from the owners of Deoldify and the creaters of CelebDFv2 dataset. 

##Dependencies

Dependencies are listed in the requirements.txt file.

##Contributing

- <a href="https://github.com/MaheenShahzad"> Maheen shahzad </a>

