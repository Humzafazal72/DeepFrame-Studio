from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate

def register(request):
    if request.method == "POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        myuser = User.objects.create_user(username, email, password)
        myuser.save()

        messages.success(request, "Your account has been successfully created")
        return redirect('login')
    
    return render(request,"register.html")

def login(request):
     if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request,user)
            return render(request, "index.html",{'username': username})
        else:
            messages.error(request,"Bad Credentials")
            return redirect('index')
            
     return redirect('index')

def signout(request):
    logout(request)
    messages.success(request,"Logged Out Successfully!")
    return redirect('index')


