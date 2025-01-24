from django.urls import path, include
from . import views

from .dash_apps.hist_app import immo_dashboard_dash

urlpatterns = [
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('contact', views.contact, name='contact'),
    path('profile', views.profile, name='profile'),
    path('resume', views.resume, name='resume')
]