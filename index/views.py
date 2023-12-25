from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'index.html')

def download(request):
    return render(request,'download.html')