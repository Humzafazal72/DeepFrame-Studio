from django.urls import path
from . import views
urlpatterns=[
    path("Add-Subtitles/",views.add_subtitles,name="add_subtitles"),
    path("To-Audio/",views.to_audio,name="to_audio"),
    path("Change-Format/",views.change_format,name="change_format"),
    path("Extract-Frames/",views.extract_frames,name="extract_frames"),
    path("Reverse/",views.reverse,name="reverse"),
    path("Add-Audio/",views.add_audio,name="add_audio"),
    path("Colourize/",views.colourize,name="colourize"),
    path("DF-Detect/",views.DF_detect,name="DF_detect"),
    path("Merge-Video/",views.merge,name="merge"),
    path("Trim-Video/",views.trim_vid,name="trim"),
    path("Change-Speed/",views.change_speed,name="change_speed"),
]
