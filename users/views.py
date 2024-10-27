from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponse, HttpResponseRedirect
from .forms import EditProfileForm, PasswordChangeForm


def home(request):
    return render(request, 'users/edit_profile.html', {})


def register_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Check if the passwords match
        if password != confirmation:
            messages.error(request, "Passwords do not match.")
            return render(request, "users/register.html", {"message": "Passwords do not match."})

        # Check if the username is unique
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "users/register.html", {"message": "Username already taken."})

        # Register the user
        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.save()

        # Redirect to login page with a success message
        messages.success(request, "Registration successful! Please log in.")
        return redirect(reverse("login"))

    # If GET request, render the registration page
    return render(request, "users/register.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in and redirect to the home page
            login(request, user)
            messages.success(request, ('Thank you for Logging in!'))
            return redirect(reverse("index"))
        else:
            # Display an error message
            messages.error(request, "Invalid username or password.")
            return render(request, "users/login.html", {"message": "Invalid username or password."})

    # If GET request, render the login page
    return render(request, "users/login.html")


def logout_user(request):
    logout(request)
    messages.success(request, ('You have been Logged Out...'))
    return HttpResponseRedirect(reverse("index"))


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, ('You Have Edited Your Profile...'))
            return redirect('home')
    else:
        form = EditProfileForm(instance=request.user)

    context = {'form': form}
    return render(request, 'users/edit_profile.html', context)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            # Stay Logged in after Password Change
            update_session_auth_hash(request, form.user)
            messages.success(request, ('You Have Edited Your Password...'))
            return redirect('home')
    else:
        form = PasswordChangeForm(user=request.user)

    context = {'form': form}
    return render(request, 'users/change_password.html', context)
