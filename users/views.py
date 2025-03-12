from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from users.forms import RegisterForm, LoginForm, CustomRegisterForm, CreateGroupForm
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User,Group,Permission
from django.contrib import messages
from django.db.models import Count
from events.models import Event,Category

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


def admin_dashboard(request):
    users = User.objects.all().order_by('-date_joined')
    groups = Group.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')

        user = User.objects.get(id=user_id)
        new_group = Group.objects.get(id=group_id)

        # Clear existing groups and set new group
        user.groups.clear()
        user.groups.add(new_group)
        user.save()

        messages.success(request, f"Role for {user.username} changed to {new_group.name}.")

        return redirect('admin-dashboard')

    context = {
        'total_users': User.objects.count(),
        'active_events': Event.objects.filter(date__gte=timezone.now()).count(),
        'total_groups': Group.objects.count(),
        'total_organizers': User.objects.filter(groups__name='Organizer').count(),
        'users': users,
        'groups': groups, # Passing groups for dropdown
    }
    return render(request, 'admin/admin_dashboard.html', context)


def roles(request):
    roles = Group.objects.annotate(
        users_count=Count('user', distinct=True),
        permissions_count=Count('permissions', distinct=True)
    )
    context = {'roles': roles}
    return render(request, 'admin/roles.html', context)


def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create-group')

    return render(request, 'admin/create_group.html', {'form': form})

def edit_role(request, role_id):
    role = Group.objects.get(id=role_id)
    form = CreateGroupForm(instance=role)
    if request.method == 'POST':
        form = CreateGroupForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Role updated successfully.")
            return redirect('roles')
        
    context = {'form': form, 'role': role}
    return render(request, 'admin/create_group.html', context)

def delete_role(request, role_id):
    if request.method == 'POST':
        task = Group.objects.get(id=role_id)
        task.delete()
        messages.success(request, 'Role Deleted Successfully')
        return redirect('roles')
    else:
        messages.error(request, 'Something went wrong')
        return redirect('roles')

def user_management(request):
    users = User.objects.annotate(role_count=Count('groups')).order_by('id')

    context = {
        'users': users
    }
    return render(request, 'admin/users.html', context)

def ban_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "banned" if not user.is_active else "unbanned"
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('user-management')

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    messages.success(request, f'User {user.username} has been deleted successfully.')
    return redirect('user-management')