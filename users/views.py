from django.utils import timezone
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, HttpResponse
from users.forms import LoginForm, CustomRegisterForm, CreateGroupForm, EditProfileForm, ChangePasswordForm, CustomPasswordResetConfirmForm, CustomPasswordResetForm
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Count
from events.models import Event
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.tokens import default_token_generator
from django.views.generic import View, TemplateView, UpdateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView, LoginView, LogoutView

User = get_user_model()

# Create your views here.

def is_admin(user):
    return user.groups.filter(name="Admin").exists()

def sign_up(request):
    form = CustomRegisterForm()
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(
                request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')
        else:
            print("Form is not valid")
    return render(request, 'register.html', {"form": form})

def sign_in(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, "signin.html", {'form': form})

class SignUpView(AccessMixin, CreateView):
    model = User
    form_class = CustomRegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('sign-in')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password1'))
        user.is_active = False
        user.save()
        messages.success(self.request, "A confirmation mail sent, please check your email")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Account Creation failed")
        return super().form_invalid(form)


class SignInView(LoginView):
    form_class=LoginForm
    template_name='signin.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else super().get_success_url()

@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
    return redirect('sign-in')

class SignOutView(LoginRequiredMixin,LogoutView):
    login_url='sign-in'

def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('sign-in')
        else:
            return HttpResponse('Invalid Id or token')
    except User.DoesNotExist:
        return HttpResponse('User not found')


class ProfileView(TemplateView):
    template_name='accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        user=self.request.user
        
        context['username']=user.username
        context['name']=user.get_full_name()
        context['email']=user.email
        context['phone']=user.phone
        context['location']=user.location
        context['bio']=user.bio
        context['profile_image']=user.profile_image
        context['member_since']=user.date_joined
        context['last_login']=user.last_login
        context['role']=user.groups.first().name if user.groups.exists() else "No role"
        
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/edit_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user

    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        print("Form is valid")
        print(form.cleaned_data)
        form.save()
        messages.success(self.request, 'Your profile has been updated successfully.')
        return redirect('profile')

class ChangePasswordView(PasswordChangeView):
    template_name='accounts/password_change.html'
    form_class=ChangePasswordForm

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'reset_password.html'
    success_url = reverse_lazy('sign-in')
    html_email_template_name = 'reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        print(context)
        return context

    def form_valid(self, form):
        messages.success(
            self.request, 'A Reset email sent. Please check your email')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'reset_password.html'
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(
            self.request, 'Password reset successfully')
        return super().form_valid(form)

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

class RolesView(LoginRequiredMixin,UserPassesTestMixin, ListView):
    login_url='no-permission'
    template_name='admin/roles.html'
    context_object_name='roles'
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def get_queryset(self):
        queryset=Group.objects.annotate(
            users_count=Count('user', distinct=True),
            permissions_count=Count('permissions', distinct=True)
        )
        return queryset

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

class CreateGroupView(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    login_url='no-permission'
    template_name='admin/create_group.html'
    success_url=reverse_lazy('create-group')
    form_class=CreateGroupForm    
    
    def form_valid(self, form):
        group = form.save()
        messages.success(self.request, f"Group {group.name} has been created successfully")
        return super().form_valid(form)
    
    
    def test_func(self):
        return is_admin(self.request.user)

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
    return redirect('no-permission')

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