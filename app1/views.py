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
from .serializers import EventSerializer, TeamSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .forms import EventForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_POST

import hashlib
import secrets
import logging

# Create your views here.
logger = logging.getLogger(__name__)

@login_required
@csrf_exempt
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()  # Save the event

            # Process team data
            num_teams = int(request.POST.get('num_teams'))
            for i in range(num_teams):
                team_name = request.POST.get('parties[' + str(i+1) + '][name]')
                team_image = request.FILES.get('parties[' + str(i+1) + '][image]')
                team = Team(name=team_name, event=event, image=team_image)
                team.save()

            return JsonResponse({'message': 'Event created successfully', 'event_id': event.event_id}, status=201)
        else:
            print(form.errors)

            return JsonResponse({'error': form.errors}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@api_view(['GET'])
def get_events(request):
    events = Event.objects.all().prefetch_related('teams')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def event_details(request, event_name):
    try:
        event = Event.objects.get(event_name=event_name)
        serializer = EventSerializer(event)
        return JsonResponse(serializer.data)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)


@login_required
def home_view(request):
    upcoming_events = list(Event.objects.values_list('event_name', flat=True))
    request.session['upcoming_events'] = upcoming_events
    return render(request, 'home.html')

def fetch_upcoming_events(request):
    upcoming_events = Event.objects.values_list('event_name', flat=True)
    request.session['upcoming_events'] = upcoming_events
    print("Upcoming Events:", upcoming_events)
    return render(request, 'home.html', {'upcoming_events': upcoming_events})

def fetch_event_details(request):
    event_name = request.GET.get('event_name')
    event = Event.objects.filter(event_name=event_name).first()
    if event:
        event_details = {
            'event_id': event.id,
            'event_purpose': event.purpose
        }
        return JsonResponse(event_details)
    else:
        return JsonResponse({'error': 'Event not found'}, status=404)

@login_required
def second_view(request):
    return render(request, 'second.html')

@login_required
def official_dashboard(request):
    # Retrieve the official's username from the session
    official_username = request.session.get('official_username')

    # Check if the official username is present in the session
    if official_username:
        try:
            # Retrieve the logged-in official's details from the database using the username
            official = Official.objects.get(Username=official_username)
            
            # Retrieve the mobile number associated with the official's Aadhar number
            government_data = GovernmentData.objects.get(aadhar_number=official.Aadhar_Number)
            mobile_number = government_data.mobile_number
            
            # Pass the official's details to the template
            context = {
                'username': official.Username,
                'full_name': official.FULLName,
                'email': official.Email,
                'phone_number': mobile_number,  # Use the retrieved mobile number
                'age': government_data.age  # Use the age from GovernmentData
            }
            return render(request, 'official_dashboard.html', context)
        except Official.DoesNotExist:
            return render(request, 'official_dashboard.html', {'error_message': 'Official details not found'})
        except GovernmentData.DoesNotExist:
            return render(request, 'official_dashboard.html', {'error_message': 'Government data not found'})
    else:
        # Redirect to the login page if the official username is not found in the session
        return redirect('official_login')

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

def logout_view(request):
    logout(request)
    return redirect('official_login')

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
                        request.session['official_username'] = official.Username
                        request.session.set_expiry(3600)  # 1 hour
                        return redirect('official_dashboard')
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
                    request.session['unique_address'] = primary_voter.unique_address
                    upcoming_events = list(Event.objects.values_list('event_name', flat=True))
                    request.session['upcoming_events'] = upcoming_events
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
                    request.session['unique_address'] = secondary_voter.unique_address
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
from django.core.serializers import serialize
def home_view(request):
    # Fetch the user's primary voter database
    try:
        primary_voter = PrimaryVoterDatabase.objects.get(user=request.user)
        # Fetch the user's government data using Aadhar number
        government_data = GovernmentData.objects.get(aadhar_number=primary_voter.aadhar_number)
        profile_data = {
            'unique_address': primary_voter.unique_address,
            'aadhar_number': primary_voter.aadhar_number,
            'age': government_data.age,  # Fetch age from government data
            'mobile_number': primary_voter.mobile_number,
        }
        upcoming_events = list(Event.objects.values_list('event_name', flat=True))
        events = Event.objects.values('event_name', 'event_id', 'event_purpose')
        request.session['upcoming_events'] = upcoming_events
        request.session['events'] = list(events)
        teams_data = {}
        for event in events:
            teams = Team.objects.filter(event_id=event['event_id'])
            team_data = serialize('json', teams)
            teams_data[event['event_id']] = team_data
        request.session['teams'] = teams_data
        print(team_data)
    except PrimaryVoterDatabase.DoesNotExist:
        profile_data = None
    except GovernmentData.DoesNotExist:
        profile_data = None
        
    return render(request, 'home.html', {'profile_data': profile_data})

def events_list(request):
    events = request.session.get('events', [])
    return JsonResponse(events, safe=False)

def event_list(request):
    # Fetch all events
    events = Event.objects.all()
    
    # Serialize event data
    event_data = []
    for event in events:
        event_data.append({
            'event_id': event.event_id,
            'event_name': event.event_name,
            'num_teams': event.num_teams,
            'event_purpose': event.event_purpose,
            'created_at': event.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string
        })

    # Return JSON response
    return JsonResponse(event_data, safe=False)

def logout_view(request):
    logout(request)
    return redirect('voter_login')

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

from rest_framework import viewsets
from .models import Event, Team
from .serializers import EventSerializer, TeamSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

def get_events(request):
    events = Event.objects.all().prefetch_related('parties')
    events_data = []
    for event in events:
        event_data = {
            'event_name': event.event_name,
            'event_purpose': event.event_purpose,
            'parties': [party.name for party in event.parties.all()]
        }
        events_data.append(event_data)
    return JsonResponse(events_data, safe=False)

