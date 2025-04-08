from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DailyMeal, Activity, AboutPage,HealthEvent
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from django.db import connection
from datetime import date
from datetime import datetime
from .forms import DailyMeal, WaterIntake, PeriodTracker, MedicationReminder, SleepMonitoring, WeightTracking, AboutPageForm
import boto3
import time
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
import random
import json
from django.views.decorators.csrf import csrf_exempt
from dietlytic_utils.calorie import calculate_bmr



# Login View (Fixed Form Handling)
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
        else:
            return render(request, "registration/login.html", {"form": form, "error": "Invalid credentials"})
    
    form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

# Register View 
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})

# Logout View
@login_required
def user_logout(request):
    logout(request)
    return redirect("login")

# Debug View (Lists All URLs)
def debug_urls(request):
    from django.urls import get_resolver
    urls = [str(url.pattern) for url in get_resolver().url_patterns]
    return HttpResponse("<br>".join(urls))  # Prints all registered URLs
 
# Home Page
def home(request):
    return render(request, 'main/home.html')

#about page
@login_required
def about(request):
    about_page, created = AboutPage.objects.get_or_create(user=request.user)
    return render(request, 'main/about.html', {'about_page': about_page})

@login_required
def edit_about(request):
    try:
        about_page = AboutPage.objects.get(user=request.user)
    except AboutPage.DoesNotExist:
        about_page = AboutPage(user=request.user)

    if request.method == "POST":
        form = AboutPageForm(request.POST, instance=about_page)
        if form.is_valid():
            form.save()
            return redirect('about')  # Redirect to the about page after saving
    else:
        form = AboutPageForm(instance=about_page)

    return render(request, 'main/edit_about.html', {'form': form})

#dashboard
@login_required
def get_health_events(request):
    events = HealthEvent.objects.filter(user=request.user)
    formatted_events = [
        {"title": event.event_name, "start": str(event.date), "time": str(event.time)}
        for event in events
    ]
    return JsonResponse(formatted_events, safe=False)

@login_required
def dashboard(request):
    """ Dashboard with Health Calendar & Event Form """
    if request.method == "POST":
        event_name = request.POST.get("event_name")
        event_date = request.POST.get("event_date")
        event_time = request.POST.get("event_time")
        description = request.POST.get("description")

        # Validate date
        if isinstance(date, str) and date.strip():
            event_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            return HttpResponse("Invalid date format", status=400)

        # Validate time
        if isinstance(time, str) and time.strip():
            event_time = datetime.strptime(time, "%H:%M").time()
        else:
            return HttpResponse("Invalid time format", status=400)

        
            
        if event_name and   event_date:
            HealthEvent.objects.create(
                user=request.user,
                event_name=event_name,
                date=datetime.strptime(date, "%Y-%m-%d"),
                time=datetime.strptime(time, "%H:%M").time() if time else None,
                description=description
            )
            return redirect("dashboard")

    return render(request, "main/dashboard.html")

# Diet Page
@login_required
def diet(request):
    meals = DailyMeal.objects.filter(user=request.user)
    return render(request, 'main/diet.html', {'meals': meals})

@login_required
def diet_plan(request):
    return render(request, 'main/diet_plan.html')

# Activity Page
@login_required
def activity(request):
    today = date.today()
    # Fetch user-specific data
    meals = DailyMeal.objects.filter(user=request.user, date=today)
    water_intake = WaterIntake.objects.filter(user=request.user, date=today).first()
    sleep_data = SleepMonitoring.objects.filter(user=request.user, date=today).first()
    period_data = PeriodTracker.objects.filter(user=request.user).first()
    medication_reminders = MedicationReminder.objects.filter(user=request.user, date=today)

    if request.method == "POST":
        print("POST Data:", request.POST)  # Debugging purpose

        # Handling Meal Tracking
        if "meal_form" in request.POST:
            meal_details = request.POST.get("meal_details")  
            if meal_details:
                DailyMeal.objects.create(user=request.user, meal_details=meal_details, date=today)

        # Handling Water Intake
        elif "water_form" in request.POST:
            water_glasses = request.POST.get("water_glasses")
            if water_glasses and water_glasses.isdigit():
                WaterIntake.objects.create(user=request.user, glasses=int(water_glasses), date=today)

        # Handling Period Tracker
        elif "period_form" in request.POST:
            last_period_date = request.POST.get("last_period_date")
            cycle_length = request.POST.get("cycle_length")

            if not last_period_date or not cycle_length:
                return HttpResponse("Error: Last period date and cycle length cannot be empty.", status=400)

            try:
                cycle_length = int(cycle_length)
                PeriodTracker.objects.update_or_create(
                    user=request.user,
                    defaults={"last_period_date": last_period_date, "cycle_length": cycle_length}
                )
            except ValueError:
                return HttpResponse("Error: Cycle length must be a number.", status=400)

        # Handling Medication Reminder
        elif "med_form" in request.POST:
            medication_name = request.POST.get("medication_name")
            medication_time = request.POST.get("medication_time")
            dosage = request.POST.get("dosage")

            if medication_name and medication_time and dosage:
                MedicationReminder.objects.create(
                    user=request.user, medication_name=medication_name, time=medication_time, dosage=dosage, date=today
                )

        # Handling Sleep Monitoring
        elif "sleep_form" in request.POST:
            sleep_hours = request.POST.get("sleep_hours")
            if sleep_hours and sleep_hours.isdigit():
                SleepMonitoring.objects.update_or_create(
                    user=request.user, date=today, defaults={"sleep_hours": int(sleep_hours)}
                )

        return redirect("activity")  # Refresh page after submission

    # Prepare context for rendering
    context = {
        "meals": meals,
        "water_intake": water_intake.glasses if water_intake else 0,
        "sleep_hours": sleep_data.sleep_hours if sleep_data else 0,
        "period_tracker": period_data,
        "medication_reminders": medication_reminders,
    }
    return render(request, "main/activity.html", context)




# Report Page
@login_required
def report(request):
    return render(request, 'main/report.html')



# S3 Upload Function
def upload_to_s3(file_name, bucket_name):
    try:
        s3_client = boto3.client('s3', region_name='eu-west-1')  # Ireland S3 Bucket
        s3_client.upload_file(file_name, bucket_name, file_name)
        return "Upload Successful"
    except Exception as e:
        return f"Upload Failed: {e}"

# CloudWatch Logging Function (With Error Handling)
def log_event_to_cloudwatch(message):
    try:
        cloudwatch_logs = boto3.client('logs', region_name='us-east-1')  # CloudWatch in US East
        cloudwatch_logs.put_log_events(
            logGroupName='your-log-group',
            logStreamName='your-stream-name',
            logEvents=[{'timestamp': int(time.time() * 1000), 'message': message}],
        )
        return "Log Sent Successfully"
    except Exception as e:
        return f"Logging Failed: {e}"


def get_activity_events(request):
    user = request.user
    events = []
    
    meals = DailyMeal.objects.filter(user=user)
    for meal in meals:
        events.append({'title': 'Meal', 'start': str(meal.date)})
    
    sleeps = SleepMonitoring.objects.filter(user=user)
    for sleep in sleeps:
        events.append({'title': f'Sleep: {sleep.sleep_hours}h', 'start': str(sleep.date)})

    return JsonResponse(events, safe=False)



# AWS SQS Setup
sqs = boto3.client('sqs', region_name='eu-west-1')
QUEUE_URL = 'https://sqs.eu-west-1.amazonaws.com/250738637992/dietlytic-queue'

def generate_diet_plan(height, weight, preference):
    """Simulate AI-generated diet plan"""
    diet_options = {
        "veg": ["Salad Bowl", "Quinoa & Chickpeas", "Fruit Smoothie", "Oatmeal", "Grilled Paneer"],
        "non_veg": ["Grilled Chicken", "Salmon with Veggies", "Egg Scramble", "Chicken Soup", "Beef Stir-fry"]
    }
    selected_dishes = random.sample(diet_options[preference], 3)
    return {"breakfast": selected_dishes[0], "lunch": selected_dishes[1], "dinner": selected_dishes[2]}

@csrf_exempt
def request_diet_plan(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            height = data.get("height")
            weight = data.get("weight")
            preference = data.get("preference", "veg")

            # Debug: Log received data
            print(f"Received: Height={height}, Weight={weight}, Preference={preference}")

            # Generate AI Diet Plan
            diet_plan = generate_diet_plan(height, weight, preference)

            # Send to SQS
            message_body = json.dumps({"height": height, "weight": weight, "preference": preference, "diet_plan": diet_plan})
            sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=message_body)

            return JsonResponse({"status": "Request sent to SQS", "diet_plan": diet_plan})
        except Exception as e:
            print("Error:", str(e))  # Debug error
            return JsonResponse({"error": "Server error occurred."}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def fetch_diet_plan(request):
    try:
        response = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=5)

        if 'Messages' in response:
            message = response['Messages'][0]
            body = json.loads(message['Body'])

            # Delete the message after reading
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=message['ReceiptHandle'])

            return JsonResponse({"status": "Success", "diet_plan": body["diet_plan"]})

        return JsonResponse({"status": "No messages in queue"})
    except Exception as e:
        print("Error:", str(e))  # Debug error
        return JsonResponse({"error": "Failed to fetch diet plan"}, status=500)
