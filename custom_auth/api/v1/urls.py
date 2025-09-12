from django.urls import (path,
                         )

from custom_auth.api.v1 import views
app_name = 'custom_auth'


urlpatterns = [
    path('auth/github/', views.github_oauth_callback, name='github-oauth'),
]