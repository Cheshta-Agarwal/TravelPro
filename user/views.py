from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import random
import time



def home(request):
    return render(request, 'index.html')


def register(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            error = "Username already exists"
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            send_mail(
                subject='Registration Successful: Welcome to TravelPro',
                message=f'Hi {username}, your account has been successfully created. Welcome to TravelPro!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('login')

    return render(request, 'registration.html', {"error": error})


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

    error = "Invalid username or password"
    return render(request, 'login.html', {"error": error})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile(request):
    return render(request, 'profile.html')


def otp_login_view(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if not user:
            error = "No user found with this email"
        else:
            otp = str(random.randint(100000, 999999))
            request.session["otp"] = otp
            request.session["otp_user_id"] = user.id
            request.session["otp_time"] = time.time()

            send_mail(
                "Your OTP for TravelPro Login",
                f"Your OTP is {otp}. It is valid for 5 minutes.",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return redirect("otp_verify")

    return render(request, "otp_login.html", {"error": error})


def otp_verify_view(request):
    error = None

    if request.method == "POST":
        otp = request.POST.get("otp")
        session_otp = request.session.get("otp")
        user_id = request.session.get("otp_user_id")
        otp_time = request.session.get("otp_time")

        if not session_otp or not user_id or not otp_time:
            return redirect("otp_login")

        if time.time() - otp_time > 300:
            request.session.flush()
            return redirect("otp_login")

        if otp != session_otp:
            error = "Invalid OTP"
            return render(request, "otp_verify.html", {"error": error})

        user = User.objects.get(id=user_id)
        login(request, user)
        request.session.flush()
        return redirect("index")

    return render(request, "otp_verify.html", {"error": error})

