from django.utils import timezone
from django.shortcuts import render, redirect
from users.forms import LoginForm, CustomRegisterForm, CreateGroupForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Count
from events.models import Event
from django.contrib.auth.decorators import user_passes_test, login_required, permission_required

# Create your views here.

def is_admin(user):
    return user.groups.filter(name="Admin").exists()

def signup(request):
    if request.method == 'GET':
        form = CustomRegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Welcome!")
            return redirect('home')
        else:
            messages.error(request, "There was an error with your registration. Please correct the form.")
        return render(request, 'register.html', {'form': form})

def sign_in(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, "signin.html", {'form': form})

@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
    return redirect('sign-in')

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related('groups').all().order_by('-date_joined')
    groups = Group.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')

        user = User.objects.get(id=user_id)
        new_group = Group.objects.get(id=group_id)
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
        'groups': groups,
    }
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def roles(request):
    roles = Group.objects.annotate(
        users_count=Count('user', distinct=True),
        permissions_count=Count('permissions', distinct=True)
    )
    context = {'roles': roles}
    return render(request, 'admin/roles.html', context)

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('create-group')
    return render(request, 'admin/create_group.html', {'form': form})

@login_required
@user_passes_test(is_admin, login_url='no-permission')
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

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def delete_role(request, role_id):
    if request.method == 'POST':
        task = Group.objects.get(id=role_id)
        task.delete()
        messages.success(request, 'Role Deleted Successfully')
        return redirect('roles')
    return redirect('no-permission')  # Redirect to no-permission for unauthorized GET requests

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def user_management(request):
    users = User.objects.prefetch_related('groups').annotate(role_count=Count('groups')).order_by('id')
    context = {
        'users': users
    }
    return render(request, 'admin/users.html', context)

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def ban_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "banned" if not user.is_active else "unbanned"
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('user-management')

@login_required
@user_passes_test(is_admin, login_url='no-permission')
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    messages.success(request, f'User {user.username} has been deleted successfully.')
    return redirect('user-management')