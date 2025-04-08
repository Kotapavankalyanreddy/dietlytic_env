from django import forms
from .models import DailyMeal, WaterIntake, PeriodTracker, MedicationReminder, SleepMonitoring, WeightTracking
from .models import AboutPage
from dietlytic_utils.validators import is_valid_mobile

class AboutPageForm(forms.ModelForm):
    class Meta:
        model = AboutPage
        fields = ['name', 'date_of_birth', 'height', 'weight', 'mobile_number']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if not is_valid_mobile(mobile_number):
            raise forms.ValidationError("Mobile number must be exactly 10 digits and numeric.")
        return mobile_number

class DailyMealForm(forms.ModelForm):
    class Meta:
        model = DailyMeal
        fields = ['meal_details']

class WaterIntakeForm(forms.ModelForm):
    class Meta:
        model = WaterIntake
        fields = ['glasses']

class PeriodTrackerForm(forms.ModelForm):
    class Meta:
        model = PeriodTracker
        fields = ['last_period_date', 'cycle_length']
        widgets = {
            'last_period_date': forms.DateInput(attrs={'type': 'date'}),
        }

class MedicationReminderForm(forms.ModelForm):
    class Meta:
        model = MedicationReminder
        fields = ['medication_name', 'time', 'dosage']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

class SleepMonitoringForm(forms.ModelForm):
    class Meta:
        model = SleepMonitoring
        fields = ['sleep_hours']

class WeightTrackingForm(forms.ModelForm):
    class Meta:
        model = WeightTracking
        fields = ['weight']
