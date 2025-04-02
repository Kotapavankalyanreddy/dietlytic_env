from django.urls import path
from .views import ( 
    register, user_login, user_logout, dashboard,
    home, report, diet, about, edit_about, get_activity_events, get_health_events,request_diet_plan, fetch_diet_plan,diet_plan
)
from .views import activity
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', home, name='home'), 
    path('login/', user_login, name='login'), 
    path('register/', register, name='register'),  
    path('logout/', user_logout, name='logout'), 
    path('dashboard/', dashboard, name='dashboard'), 
    path("api/get_health_events/", get_health_events, name="get_health_events"),
    path('activity/', activity, name='activity'), 
    path('api/get_activity_events/', get_activity_events, name='get_activity_events'),
    path('report/', report, name='report'), 
    path('diet/', diet, name='diet'), 
    path('diet_plan/', diet_plan, name='diet_plan'),     
    path('request-diet/', request_diet_plan, name='request_diet'),
    path('fetch-diet/', fetch_diet_plan, name='fetch_diet'),
    path('about/', about, name='about'), 
    path('about/edit/', edit_about, name='edit_about'),  

]
