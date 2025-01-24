from django.shortcuts import render

def home(request): 
    return render(request, 'app/welcome.html')

def dashboard(request):
    return render(request, 'app/dashboard.html')

def contact(request):
    return render(request, 'app/contact.html')

def profile(request):
    return render(request, 'app/profile.html')

def resume(request):
    return render(request, 'app/resume.html')