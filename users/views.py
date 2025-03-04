from django.shortcuts import render, redirect
from users.forms import RegisterForm
from django.contrib.auth import login,logout,authenticate

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

def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(username=username,password=password)
        
        if user is not None:
            login(request,user)
            return redirect('main_home')
        else:
            return render(request,'signin.html', {'error': 'Invalid Username or Password'})
    return render(request,'signin.html')