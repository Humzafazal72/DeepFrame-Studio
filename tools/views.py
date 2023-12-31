import os
import cv2
import math
import ffmpeg
import random
import shutil
import tensorflow
import numpy as np
from PIL import Image
from mtcnn.mtcnn import MTCNN
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from .Colorization.deoldify import visualize
from moviepy.editor import VideoFileClip, concatenate_videoclips

x_tuned = tensorflow.keras.models.load_model(r"models\fine_tuned_meso.h5")

colorizer = visualize.get_video_colorizer()

def findEuclideanDistance(source_representation, test_representation):
    euclidean_distance = source_representation - test_representation
    euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
    euclidean_distance = np.sqrt(euclidean_distance)
    return euclidean_distance


def alignment_procedure(img, left_eye, right_eye, nose):
    left_eye_x, left_eye_y = left_eye
    right_eye_x, right_eye_y = right_eye

    center_eyes = (
        int((left_eye_x + right_eye_x) / 2),
        int((left_eye_y + right_eye_y) / 2),
    )

    if False:
        img = cv2.circle(img, (int(left_eye[0]), int(left_eye[1])), 2, (0, 255, 255), 2)
        img = cv2.circle(img, (int(right_eye[0]), int(right_eye[1])), 2, (255, 0, 0), 2)
        img = cv2.circle(img, center_eyes, 2, (0, 0, 255), 2)
        img = cv2.circle(img, (int(nose[0]), int(nose[1])), 2, (255, 255, 255), 2)

    if left_eye_y > right_eye_y:
        point_3rd = (right_eye_x, left_eye_y)
        direction = -1  # rotate same direction to clock
    else:
        point_3rd = (left_eye_x, right_eye_y)
        direction = 1  # rotate inverse direction of clock
    a = findEuclideanDistance(np.array(left_eye), np.array(point_3rd))
    b = findEuclideanDistance(np.array(right_eye), np.array(point_3rd))
    c = findEuclideanDistance(np.array(right_eye), np.array(left_eye))

    if (
        b != 0 and c != 0
    ):  # this multiplication causes division by zero in cos_a calculation
        cos_a = (b * b + c * c - a * a) / (2 * b * c)

        cos_a = min(1.0, max(-1.0, cos_a))

        angle = np.arccos(cos_a)  # angle in radian
        angle = (angle * 180) / math.pi  # radian to degree
        if direction == -1:
            angle = 90 - angle

        img = Image.fromarray(img)
        img = np.array(img.rotate(direction * angle))

    return img  # return img anyway


def process_video(input_video_path, output_face_folder, video_name):
    cap = cv2.VideoCapture(input_video_path)

    detector = MTCNN()

    iter = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if iter % 10 == 0:
            faces = detector.detect_faces(frame)
            if faces and faces[0]["box"] != []:
                img_aligned = alignment_procedure(
                    frame,
                    right_eye=faces[0]["keypoints"]["right_eye"],
                    left_eye=faces[0]["keypoints"]["left_eye"],
                    nose=faces[0]["keypoints"]["nose"],
                )
                img_aligned = img_aligned[:, :, ::-1]
                img_aligned = cv2.cvtColor(img_aligned, cv2.COLOR_BGR2RGB)

                align_faces = detector.detect_faces(img_aligned)
                if align_faces and align_faces[0]["box"] != []:
                    x, y, width, height = align_faces[0]["box"]
                    face_image = img_aligned[y : y + height, x : x + width]

                    aligned_face_filename = os.path.join(
                        output_face_folder, f"{iter}.jpg"
                    )
                    cv2.imwrite(aligned_face_filename, face_image)

        iter += 1
    cap.release()

def concatenate(video_clip_paths, output_path, method="compose"):
    # create VideoFileClip object for each video file
    clips = [VideoFileClip(c) for c in video_clip_paths]
    if method == "reduce":
        # calculate minimum width & height across all clips
        min_height = min([c.h for c in clips])
        min_width = min([c.w for c in clips])
        # resize the videos to the minimum
        clips = [c.resize(newsize=(min_width, min_height)) for c in clips]
        # concatenate the final video
        final_clip = concatenate_videoclips(clips)
    elif method == "compose":
        # concatenate the final video with the compose method provided by moviepy
        final_clip = concatenate_videoclips(clips, method="compose")
    # write the output video file
    final_clip.write_videofile(output_path)

def process_img(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (256, 256))
    image = image / 255.0
    image = np.expand_dims(image, axis=0)
    return image

def add_subtitles(request):
    if request.method == "POST":
        input_vid = request.FILES.get("input_vid")
        subs = request.FILES.get("input_subs")

        sub_name = subs.name
        file_extension = sub_name.split(".")[-1].lower()
        if file_extension not in [
            "srt",
            "sub",
            "vtt",
            "txt",
            "ass",
            "ssa",
            "xml",
            "idx",
            "pgs",
            "dfxp",
            "ttml",
        ]:
           messages.warning(request,"Please ensure the subtitle file is in valid format.")
           return redirect('add_subtitles')

        vid_name = input_vid.name
        video_content = input_vid.read()
        original_video_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "add_subs", vid_name
        )
        with open(original_video_path, "wb") as file:
            file.write(video_content)

        sub_content = subs.read()
        sub_path = f"inputs\\others\\subs\\{sub_name}"
        with open(sub_path, "wb") as file:
            file.write(sub_content)

        new_name = (
            vid_name.split(".")[0]
            + str(random.randint(1, 100000))
            + "."
            + vid_name.split(".")[1]
        )
        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "add_subs", new_name
        )

        try:
            ffmpeg_vid = ffmpeg.input(original_video_path)
            ffmpeg_audio = ffmpeg_vid.audio
            ffmpeg.concat(
                ffmpeg_vid.filter("subtitles", sub_path), ffmpeg_audio, v=1, a=1
            ).output(output_path).run()
        except ffmpeg.Error as e:
           messages.warning(request,"There was an error processing the video. please ensure there isn't a '.' in the video name.")
           return redirect('add_subtitles')

        remaining_path = f"add_subs\\{new_name}"
        return render(
            request,
            "download.html",
            {"message": "Subtitles Added Successfully", "path": remaining_path},
        )

    return render(request, "add_sub.html")


def to_audio(request):
    if request.method == "POST":
        input_vid = request.FILES.get("input_vid")
        vid_name_full = input_vid.name
        vid_name = vid_name_full.split(".")[0]

        vid_content = input_vid.read()
        orignal_vid_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "to_audio", vid_name_full
        )
        with open(orignal_vid_path, "wb") as file:
            file.write(vid_content)

        new_name = vid_name + str(random.randint(1, 100000)) + ".mp3"
        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "audio", new_name
        )
        try:
            ffmpeg.input(orignal_vid_path).output(output_path).run()
        except ffmpeg.Error as e:
            messages.warning(request,"There was an error processing the video. Please try again later or try changing the video format.")
            return redirect('to_audio')

        remaining_path = f"audio\\{new_name}"
        return render(
            request,
            "download.html",
            {
                "message": "Subtitles Added Successfully!",
                "path": remaining_path,
                "audioo": True,
            },
        )

    return render(request, "to_audio.html")


def change_format(request):
    if request.method == "POST":
        selected_format = request.POST.get("format")
        input_vid = request.FILES.get("input_vid")
        vid_name_full = input_vid.name
        vid_name = vid_name_full.split(".")[0]

        vid_content = input_vid.read()
        orignal_vid_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "convert", vid_name_full
        )
        with open(orignal_vid_path, "wb") as file:
            file.write(vid_content)

        new_name = vid_name + str(random.randint(1, 100000)) + selected_format
        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "convert", new_name
        )
        try:
            ffmpeg.input(orignal_vid_path).output(output_path).run()
        except ffmpeg.Error as e:
            messages.warning(request,"There was an error processing the video. Please ensure there isn't '.' in the video name.")
            return redirect('change_format')        
        
        remaining_path = f"convert\\{new_name}"
        return render(
            request,
            "download.html",
            {"message": "Video Format Conversion Successful!", "path": remaining_path},
        )

    return render(request, "change_format.html")


def extract_frames(request):
    if request.method == "POST":
        input_vid = request.FILES.get("input_vid")
        vid_name_full = input_vid.name
        vid_name = vid_name_full.split(".")[0]

        vid_content = input_vid.read()
        original_vid_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "extract_frames", vid_name_full
        )
        with open(original_vid_path, "wb") as file:
            file.write(vid_content)

        new_name = vid_name + str(random.randint(1, 100000))
        os.mkdir(
            os.path.join(
                settings.BASE_DIR,
                "index",
                "static",
                "outputs",
                "extract_frames",
                new_name,
            )
        )
        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "extract_frames", new_name
        )
        try:
            ffmpeg.input(original_vid_path).output(
                os.path.join(output_path, "frame%d.png")
            ).run()

        except ffmpeg.Error as e:
            messages.warning(request,"There was an error processing the video. Please ensure the video name does not contain '.' in it.")
            return redirect('extract-frames')

        zip_path = f"index\\static\\outputs\\extract_frames\\{new_name}"

        shutil.make_archive(zip_path, "zip", output_path)
        shutil.rmtree(output_path)

        remaining_path = f"extract_frames\\{new_name+'.zip'}"
        return render(
            request,
            "download.html",
            {
                "message": "Frame Extraction Successful!",
                "path": remaining_path,
                "name": new_name,
            },
        )

    return render(request, "extract_frames.html")


def reverse(request):
    if request.method == "POST":
        input_vid = request.FILES.get("input_vid")
        vid_name_full = input_vid.name
        vid_name = vid_name_full.split(".")[0]
        extension = vid_name_full.split(".")[1]

        vid_content = input_vid.read()
        orignal_vid_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "reverse", vid_name_full
        )
        with open(orignal_vid_path, "wb") as file:
            file.write(vid_content)

        new_name = vid_name + str(random.randint(1, 100000)) + "." + extension
        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "reverse", new_name
        )
        try:
            ffmpeg.input(orignal_vid_path).output(output_path, vf="reverse", af="areverse").run()
        except ffmpeg.Error as e:
            messages.warning(request,"There was an error processing the video. Please the ensure the video doesn't have '.' in the name.")
            return redirect('reverse')
        
        remaining_path = f"reverse\\{new_name}"
        return render(
            request,
            "download.html",
            {"message": "Video Reversed Successfully!", "path": remaining_path},
        )
    return render(request, "reverse.html")


def add_audio(request):
    if request.method == "POST":
        input_vid = request.FILES.get("input_vid")
        input_audio = request.FILES.get("input_audio")
        vid_name_full = input_vid.name
        vid_name = vid_name_full.split(".")[0]
        extension = vid_name_full.split(".")[1]
        audio_name_full = input_audio.name

        vid_content = input_vid.read()
        orignal_vid_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "add_audio", vid_name_full
        )
        with open(orignal_vid_path, "wb") as file:
            file.write(vid_content)

        audio_content = input_audio.read()
        orignal_audio_path = os.path.join(
            settings.BASE_DIR, "inputs", "others", "audio", audio_name_full
        )
        with open(orignal_audio_path, "wb") as file:
            file.write(audio_content)

        new_name = vid_name + str(random.randint(1, 100000)) + "." + extension

        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "add_audio", new_name
        )
        try:
            ffmpeg.concat(
                ffmpeg.input(orignal_vid_path).video,
                ffmpeg.input(orignal_audio_path),
                v=1,
                a=1,
            ).output(output_path).run()
        except ffmpeg.Error as e:
            messages.warning(request,"There was an error processing the video. Please ensure there isn't '.' in the video name.")
            return redirect('add_audio')
        
        remaining_path = f"add_audio\\{new_name}"
        return render(
            request,
            "download.html",
            {"message": "Audio Added Sucessfully!", "path": remaining_path},
        )

    return render(request, "add_audio.html")


def merge(request):
    if request.method == "POST":
        input_vids = request.FILES.getlist("input_vids")
        files=[]

        for input_vid in input_vids:
            vid_name=input_vid.name
            vid_content = input_vid.read()
            individual_vid_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "merge", vid_name
            )
            with open(individual_vid_path, "wb") as file:
                file.write(vid_content)
            files.append(individual_vid_path)

        new_name="merge" + str(random.randint(1, 100000)) + ".mp4"
        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "merge", new_name
        )   
        try:
            concatenate(files, output_path, method="compose")          
        except:
            messages.warning(request,"There was an error processing the video. Please ensure there wasn't '.' in the video name and videos are in mp4 format.")            
            return redirect('merge')
        remaining_path = f"merge\\{new_name}"
        return render(
            request,
            "download.html",
            {"message": "Videos Merged Sucessfully!", "path": remaining_path},
        )


    return render(request, "merge_vids.html")

def trim_vid(request):
    if request.method == "POST":
        input_vid = request.FILES.get("input_vid")
        hh1 = str(request.POST["hh1"])
        mm1 = str(request.POST["mm1"])
        ss1 = str(request.POST["ss1"])
        hh2 = str(request.POST["hh2"])
        mm2 = str(request.POST["mm2"])
        ss2 = str(request.POST["ss2"])

        start = hh1 + (":") + mm1 + (":") + ss1 
        endd = hh2 + (":") + mm2 + (":") + ss2 

        print(start,endd)

        vid_name = input_vid.name
        vid_content = input_vid.read()
        orignal_vid_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "trim", vid_name
        )
        with open(orignal_vid_path, "wb") as file:
            file.write(vid_content)

        new_name = vid_name.split(".")[0] + str(random.randint(1, 100000)) + "." + vid_name.split(".")[1]
        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "trim", new_name
        )
        try:
            (
                ffmpeg.input(orignal_vid_path, ss=start, to=endd)
                .output(output_path)
                .run()
            )
        except ffmpeg.Error as e:
            messages.warning(request,"There was an error processing the video. Please ensure the time stamp given was valid and there wasn't '.' in the video name.")
            return redirect('trim')

        remaining_path = f"trim\\{new_name}"
        return render(
            request,
            "download.html",
            {"message": "Video Trimed Sucessfully!", "path": remaining_path},
        )

    return render(request, "trim.html")


def change_speed(request):
    if request.method == "POST":
        input_vid = request.FILES.get("input_vid")
        speed_factor = float(request.POST["speed"])
        vid_name_full = input_vid.name
        vid_name = vid_name_full.split(".")[0]
        extension = vid_name_full.split(".")[1]

        vid_content = input_vid.read()
        orignal_vid_path = os.path.join(
            settings.BASE_DIR, "inputs", "vids", "speed", vid_name_full
        )
        with open(orignal_vid_path, "wb") as file:
            file.write(vid_content)

        new_name = vid_name + str(random.randint(1, 100000)) + "." + extension
        output_path = os.path.join(
            settings.BASE_DIR, "index", "static", "outputs", "speed", new_name
        )
        try:
            (
                ffmpeg.input(orignal_vid_path)
                .output(
                    output_path,
                    vf="setpts=" + str(1 / speed_factor) + "*PTS",
                    af="atempo=" + str(speed_factor),
                )
                .run()
            )
        except ffmpeg.Error as e:
            messages.warning(request,"There was an error processing the video. Please ensure there isn't '.' in the video name.")
            return redirect('change_speed')
        
        remaining_path = f"Speed\\{new_name}"
        return render(
            request,
            "download.html",
            {"message": "Speed Change Successful!", "path": remaining_path},
        )

    return render(request, "change_speed.html")


def colourize(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            input_vid = request.FILES.get("input_vid")
            vid_name = input_vid.name

            vid_content = input_vid.read()
            orignal_vid_path = os.path.join(
                settings.BASE_DIR,'index','static' , "bw", vid_name
            )
            with open(orignal_vid_path, "wb") as file:
                file.write(vid_content)

            colorizer._colorize_from_path(orignal_vid_path, render_factor=21)
            shutil.rmtree(r'.\index\static\outputs\color\bwframes')
            shutil.rmtree(r'.\index\static\outputs\color\colorframes')
            return render(
                request,
                "download.html",
                {"message": "Video Coloured Successfully!",'original_file':vid_name},
            )

        return render(request, "colourize.html")
    
    else:
        messages.warning(request,'You must be logged in to use AI features.')
        return redirect('index')    



def DF_detect(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if os.path.exists(os.path.join(settings.BASE_DIR,'index','static','outputs','DF_faces')):
                shutil.rmtree(os.path.join(settings.BASE_DIR,'index','static','outputs','DF_faces'))
            status=[]
            images=[]

            input_vid = request.FILES.get("input_vid")
            vid_name = input_vid.name

            vid_content = input_vid.read()
            original_vid_path = os.path.join(
                settings.BASE_DIR, "inputs", "vids", "DF", vid_name
            )
            with open(original_vid_path, "wb") as file:
                file.write(vid_content)

            os.mkdir(os.path.join(settings.BASE_DIR,'index','static','outputs','DF_faces'))
            output_face_path=os.path.join(settings.BASE_DIR,'index','static','outputs','DF_faces')
            process_video(original_vid_path, output_face_path, vid_name)
            for i in os.listdir(output_face_path):
                images.append(i)
                img_path = os.path.join(output_face_path, i)
                img = process_img(img_path)
                pred = x_tuned.predict(img)
                if pred[0] > 0.5:
                    status.append(1)   
                elif pred[0] < 0.5:
                    status.append(0)

            result='No DeepFake Detected!'
            if sum(status) >= len(status)/2:
                result='DeepFake Detected!!' 

            return render(
            request,
            "download.html",
            {"message": "Check Complete!",'result':result,'vid_name':vid_name,
             'anomalies':sum(status),'total':len(status),
              'status':status, 'images':images },
            )

        return render(request, "DF_detect.html")

    else:
        messages.warning(request,'You must be logged in to use AI features.')
        return redirect('index')

