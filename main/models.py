from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    height = models.FloatField()
    weight = models.FloatField()
    contact_number = models.CharField(max_length=15)

class DailyMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_details = models.CharField(max_length=255)  
    date = models.DateField(auto_now_add=True)
    calorie_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.meal_details} - {self.date}"

class WaterIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    glasses = models.IntegerField()
    

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.glasses} glasses"

class PeriodTracker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_period_date = models.DateField(null=True, blank=True)  
    cycle_length = models.IntegerField()

    def __str__(self):
        return f"Period on {self.last_period_date}, Cycle: {self.cycle_length} days"

class MedicationReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    medication_name = models.CharField(max_length=255)
    time = models.TimeField()
    dosage = models.CharField(max_length=255)

class SleepMonitoring(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    sleep_hours = models.FloatField()

class WeightTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField()



def validate_mobile_number(value):
    if not value.isdigit():
        raise ValidationError("Mobile number must contain only digits.")
    if len(value) != 10:
        raise ValidationError("Mobile number must be exactly 10 digits.")
    
class AboutPage(models.Model): 
    id = models.AutoField(primary_key=True)  
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=False, blank=False, default="Default Title") 
    content = models.TextField(null=False, blank=False, default="Default Content") 
    updated_at = models.DateTimeField(auto_now=True) 
    name = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    mobile_number = models.CharField(max_length=10, validators=[validate_mobile_number]   )

    def __str__(self):
        return self.user.username

    
class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    meal_details = models.TextField()
    calorie_count = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    exercise_details = models.TextField()
    calories_burned = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    



class HealthEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_time = models.TimeField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.event_name} on {self.event_date} at {self.event_time}"