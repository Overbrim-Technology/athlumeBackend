from django.urls import path, include

urlpatterns = [
    # Route traffic to Version 1 configuration
    path('v1/', include('api.v1.urls')),
    
    # Future proofing:
    # path('v2/', include('api.v2.urls')), 
]