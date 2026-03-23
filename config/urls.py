"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import confirm_email
from django.views.generic import TemplateView

admin.site.site_header = 'Athlume'
admin.site.site_title = 'Athlume Profile'


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Login, Logout, Password Reset, Password Change
    path('api/auth/', include('dj_rest_auth.urls')),

    # 2. Signup / Registration
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # This URL is what is actually sent in the email
    path('api/v1/auth/registration/account-confirm-email/<str:key>/', 
         confirm_email, 
         name='account_confirm_email'),

    # This name must be 'password_reset_confirm' exactly.
    # The 'uidb64' and 'token' are the parameters Django injects into the email.
    re_path(
        r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        TemplateView.as_view(template_name="password_reset_confirm.html"),
        name='password_reset_confirm'),
    
    # 3. Your App Endpoints
    path('api/', include('api.urls')), 
]
