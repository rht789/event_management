from django.urls import path
from users.views import signup,sign_in,sign_out

urlpatterns = [
    path('sign-up/', signup, name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-out/', sign_out, name='sign-out'),
]

