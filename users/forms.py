from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import Permission,Group
from events.forms import StyledFormMixin
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','password1','password2','email']
        
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

class CustomRegisterForm(StyledFormMixin,forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2','phone','profile_image']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError("Please enter an email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already associated with an exissting acount")
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        errors = []
        
        if not password1:
            errors.append("Password is required.")
        if len(password1) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in password1):
            errors.append("Password must contain at least one uppercase letter.")
        if not any(char.isdigit() for char in password1):
            errors.append("Password must contain at least one number.")
        if not any(char in '!@#$%^&*()' for char in password1):
            errors.append("Password must contain at least one special character (e.g., !@#$%^&*()).")
        if errors:
            raise forms.ValidationError(errors)
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1!= password2:
            raise forms.ValidationError("Password Do Not Match")
        return cleaned_data
    
class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        
class CreateGroupForm(StyledFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Permission'
    )
    
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': 'Role Name',
            'permissions': 'Role Permissions'
        }
        
class EditProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'bio', 'profile_image','phone','location']
    widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_image'].widget.attrs.update({'class': 'hidden'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'e.g., 1234567890'})
        self.fields['location'].widget.attrs.update({'placeholder': 'e.g., New York, USA'})
        
class ChangePasswordForm(StyledFormMixin,PasswordChangeForm):
    pass

class CustomPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass

class CustomPasswordResetConfirmForm(StyledFormMixin, SetPasswordForm):
    pass