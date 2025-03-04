from django.urls import path
from users.views import signup

urlpatterns = [
    path('sign-up/', signup, name='sign-up'),
]

