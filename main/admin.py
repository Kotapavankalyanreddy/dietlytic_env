from django.contrib import admin
from .models import AboutPage

class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'date_of_birth', 'height', 'weight', 'mobile_number')  
    search_fields = ('user__username', 'name', 'mobile_number')

admin.site.register(AboutPage, AboutPageAdmin)
