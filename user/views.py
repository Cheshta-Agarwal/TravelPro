
from django.shortcuts import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings


# Create your views here
def home(request):
    return render(request,'index.html')


def register(request):
    error=None
    if request.method == 'POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        phone=request.POST['phone']
    
        if User.objects.filter(username=username).exists():
            error="Username already exists"
        else:
            user=User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
    
        send_mail(
            subject='Registraion Successful: Welcome to TravelPro',
            message=f'Hi {username}, your account has been successfully created. Welcome to TravelPro!',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,

        )
        return redirect('login')
    return render(request,'registration.html',{"error":error})

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

   
    user = authenticate(
        username=request.POST.get('username'),
        password=request.POST.get('password')
    )

    if user is not None:
        login(request, user)
        return redirect('index')
    else:
        error = "Invalid username or password"
        return render(request, 'login.html', {"error": error})

def logout_view(request):
    request.session.flush()
    return redirect('index')

@login_required
def profile(request):
    return render(request,'profile.html')

