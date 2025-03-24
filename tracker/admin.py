from django.contrib import admin
from .models import UserProfile, UserStats, GitHubStats

admin.site.register(UserProfile)
admin.site.register(UserStats)
admin.site.register(GitHubStats)
