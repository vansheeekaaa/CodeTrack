from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User

from tracker.utils.fetch_github import fetch_github_data
from .models import UserProfile, UserStats
from .forms import UserProfileForm
from .utils.fetch_leetcode import fetch_leetcode_data
from .utils.fetch_gfg import fetch_gfg_data

def extract_username(url):
    return url.rstrip("/").split("/")[-1] if url else None

def merge_heatmaps(*heatmaps):
    merged_heatmap = {}
    for heatmap in heatmaps:
        for date, count in heatmap.items():
            merged_heatmap[date] = merged_heatmap.get(date, 0) + count
    return merged_heatmap

@login_required
def dashboard(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile:
        return redirect('edit_profile')

    user_stats = UserStats.objects.filter(user=user_profile).first()
    if not user_stats:
        user_stats = UserStats(user=user_profile)  # Initialize with default values

    return render(request, "dashboard.html", {"user_stats": user_stats})

def user_login(request):
    if request.method == "POST":
        email, password = request.POST.get("email"), request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid email or password")
    return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        email, password = request.POST.get("email"), request.POST.get("password")
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists")
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            login(request, user)
            return redirect("dashboard")
    return render(request, "signup.html")

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def edit_profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_stats, _ = UserStats.objects.get_or_create(user=user_profile)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            
            # Fetch data from LeetCode and GFG
            leetcode_data = fetch_leetcode_data(extract_username(user_profile.leetcode_link))
            gfg_data = fetch_gfg_data(extract_username(user_profile.gfg_link))
            
            # Merge and update stats
            new_data = {
                "Easy": leetcode_data.get("difficultyCounts", {}).get("Easy", 0) + gfg_data.get("difficultyCounts", {}).get("Easy", 0),
                "Medium": leetcode_data.get("difficultyCounts", {}).get("Medium", 0) + gfg_data.get("difficultyCounts", {}).get("Medium", 0),
                "Hard": leetcode_data.get("difficultyCounts", {}).get("Hard", 0) + gfg_data.get("difficultyCounts", {}).get("Hard", 0),
                "Total": leetcode_data.get("difficultyCounts", {}).get("Total", 0) + gfg_data.get("difficultyCounts", {}).get("Total", 0),
                "Topics": {},  # If topic-wise data is available, merge here
                "Heatmap": merge_heatmaps(
                    leetcode_data.get("heatmap", {}),
                    gfg_data.get("heatmap", {})
                ),
            }

            # ✅ Update user stats properly
            user_stats.update_from_platform(new_data)

            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard")
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, "edit_profile.html", {"form": form})