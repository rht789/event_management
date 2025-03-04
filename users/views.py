from django.shortcuts import render, redirect
from users.forms import RegisterForm

# Create your views here.
def signup(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
        return render(request, 'register.html', {'form': form})
