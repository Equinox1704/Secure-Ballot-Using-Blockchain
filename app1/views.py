from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .management.commands.populate_gov_db import Command
from app1.models import GovernmentData, PrimaryVoterDatabase, SecondaryVoterDatabase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
from django import forms
from django.contrib import messages
from .models import Official

import hashlib
import secrets

# Create your views here.
# @login_required(login_url='login')
@login_required
def home_view(request):
    # Your logic for the home page view
    return render(request, 'home.html')

@login_required
def second_view(request):
    return render(request, 'second.html')

@login_required
def official_home_view(request):
    return render(request, 'official_home.html')

def voter_login(request):
    return render(request, 'voter_login.html')

def verify_otp1_view(request):
    return render(request, 'verify_otp1.html')

def verify_otp2_view(request):
    return render(request, 'verify_otp2.html')

def verify_otp3_view(request):
    return render(request, 'verify_otp3.html')

def official_login(request):
    return render(request, 'official_login.html')

def index_view(request):
    return render(request, 'index.html')

def whoru(request):
    return render(request, 'whoru.html')

def face_capture(request):
    return render(request, 'face_capture.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        aadhar_number = request.POST.get('aadhar_number')
        password = request.POST.get('password')

        # Check if the provided username and Aadhar number are for an official
        try:
            if username:
                official = Official.objects.get(Username=username, Aadhar_Number=aadhar_number)
                if official and check_password(password, official.Password):
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('verify-otp3')
                    else:
                        error_message = 'Invalid username or password'
                        return render(request, 'official_login.html', {'error_message': error_message})
        except Official.DoesNotExist:
            pass

        # If not an official, check if it's a primary voter
        try:
            if aadhar_number:
                primary_voter = PrimaryVoterDatabase.objects.get(aadhar_number=aadhar_number)
                hashed_password = primary_voter.primary_pass
                user = authenticate_voter('primary', aadhar_number, password)
                if user:
                    login(request, user)
                    return redirect('verify-otp1')
        except PrimaryVoterDatabase.DoesNotExist:
            pass

        # If not a primary voter, check if it's a secondary voter
        try:
            if aadhar_number:
                secondary_voter = SecondaryVoterDatabase.objects.get(aadhar_number=aadhar_number)
                hashed_password = secondary_voter.secondary_pass
                user = authenticate_voter('secondary', aadhar_number, password)
                if user:
                    login(request, user)
                    return redirect('verify-otp2')
        except SecondaryVoterDatabase.DoesNotExist:
            pass

        # If none of the above conditions are met, return an error message
        error_message = 'User does not exist or Incorrect password'
        return render(request, 'voter_login.html', {'error_message': error_message})

    # If the request method is not POST, render the voter_login.html template
    return render(request, 'voter_login.html')

def authenticate_voter(voter_type, aadhar_number, password):
    if voter_type == 'primary':
        try:
            voter = PrimaryVoterDatabase.objects.get(aadhar_number=aadhar_number)
        except PrimaryVoterDatabase.DoesNotExist:
            return None
    elif voter_type == 'secondary':
        try:
            voter = SecondaryVoterDatabase.objects.get(aadhar_number=aadhar_number)
        except SecondaryVoterDatabase.DoesNotExist:
            return None

    if check_password(password, voter.primary_pass if voter_type == 'primary' else voter.secondary_pass):
        return voter.user
    else:
        return None

def validate_login(request, aadhar_number, password):
    try:
        voter = VoterData.objects.get(aadhar_number=aadhar_number, primary_password=password)
        return JsonResponse({'success': True, 'passwordType': 'primary'})
    except VoterData.DoesNotExist:
        try:
            voter = VoterData.objects.get(aadhar_number=aadhar_number, secondary_password=password)
            return JsonResponse({'success': True, 'passwordType': 'secondary'})
        except VoterData.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Aadhar number or password'})

def LogoutPage(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        aadhar_number = request.POST.get('aadhar_number')
        primary_password = request.POST.get('primary_password')
        secondary_password = request.POST.get('secondary_password')

        try:
            gov_data = GovernmentData.objects.get(aadhar_number=aadhar_number)
        except GovernmentData.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Aadhar number not found in database'})

        # Check if age is greater than or equal to 18
        if gov_data.age < 18:
            return JsonResponse({'success': False, 'message': 'You must be 18 years or older to sign up.'})

        # Extract mobile number from government database
        mobile_number = gov_data.mobile_number

        try:
            # Create a new User object (without using create_user)
            user = User.objects.create_user(username=aadhar_number, password=primary_password)

            # Generate a unique address for the voter
            unique_address = get_random_string(length=32)  # Adjust length as needed

            # Create a corresponding PrimaryVoterDatabase object
            primary_voter = PrimaryVoterDatabase.objects.create(
                user=user,
                unique_address=unique_address,
                aadhar_number=aadhar_number,
                mobile_number=mobile_number,
                primary_pass=make_password(primary_password)
            )

            # Create a corresponding SecondaryVoterDatabase object
            secondary_voter = SecondaryVoterDatabase.objects.create(
                user=user,
                unique_address=unique_address,
                aadhar_number=aadhar_number,
                mobile_number=mobile_number,
                secondary_pass=make_password(secondary_password)
            )

            # Redirect to login form after successful registration
            return redirect('voter_login')

        except Exception as e:
            print("Error creating or saving VoterDatabase object:", e)
            return JsonResponse({'success': False, 'message': 'Error creating or saving voter account'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def generate_otp():
    return "56"

def official_signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        aadhar_number = request.POST.get('aadhar_number')
        password = request.POST.get('password')

        try:
            # Check if Aadhar number exists in the government database
            gov_data = GovernmentData.objects.get(aadhar_number=aadhar_number)
        except GovernmentData.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Aadhar number not found in database'})

        # Check if age is greater than or equal to 18
        if gov_data.age < 18:
            return JsonResponse({'success': False, 'message': 'You must be 18 years or older to sign up.'})

        try:
            # Create a new User object
            user = User.objects.create_user(username=username, email=email, password=password)

            # Create a corresponding Official object
            official = Official(
                FULLName=full_name,
                Username=username,
                Email=email,
                Aadhar_Number=aadhar_number,
                Password=make_password(password)
            )
            official.save()
            
            return redirect('official_login')

        except Exception as e:
            print("Error creating or saving Official object:", e)
            return JsonResponse({'success': False, 'message': 'Error creating or saving official account'})

    return render(request, 'official_login')

def validate_aadhar(request, aadhar_number):
    # Check if Aadhar number exists in the government database
    if GovernmentData.objects.filter(aadhar_number=aadhar_number).exists():
        return JsonResponse({'success': True, 'message': 'Aadhar number is valid.'})
    else:
        return JsonResponse({'success': False, 'message': 'Aadhar number not found in database.'})