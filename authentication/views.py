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
        return redirect('index')
    
    return render(request,"register.html")

def loginn(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request,"Bad Credentials")
            return redirect('index')
            
    return redirect('index')

def signout(request):
    logout(request)
    return redirect('index')


