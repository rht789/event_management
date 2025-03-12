from django.shortcuts import render, redirect
from users.forms import RegisterForm, LoginForm, CustomRegisterForm
from django.contrib.auth import login,logout,authenticate

# Create your views here.
def signup(request):
    if request.method == 'GET':
        form = CustomRegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
        return render(request, 'register.html', {'form': form})

def sign_in(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main-home')
    return render(request, "signin.html", {'form': form})

def sign_out(request):
    if request.method == 'POST':
        logout(request)
    return redirect('sign-in')