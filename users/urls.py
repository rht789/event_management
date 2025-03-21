from django.urls import path
from users.views import sign_up,sign_in,sign_out,admin_dashboard,roles,create_group,edit_role,delete_role,user_management,ban_user,delete_user,activate_user

urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-out/', sign_out, name='sign-out'),
    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('admin/dashboard', admin_dashboard, name='admin-dashboard'),
    path('admin/roles/', roles, name='roles'),
    path('admin/create-group/', create_group, name='create-group'),
    path('admin/edit-role/<int:role_id>/', edit_role, name='edit-role'),
    path('admin/delete-role/<int:role_id>/', delete_role, name='delete-role'),
    path('admin/users/', user_management, name='user-management'),
    path('admin/users/ban/<int:user_id>/', ban_user, name='ban-user'),
    path('admin/users/delete/<int:user_id>/', delete_user, name='delete-user')
]

