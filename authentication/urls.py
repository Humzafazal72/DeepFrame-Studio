from django.urls import path
from . import views

urlpatterns=[
    path("",views.loginn,name="login"),
    path("register/",views.register,name="register"),
    path("signout/",views.signout,name="logout"),
]