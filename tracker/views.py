import json
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from tracker.utils.fetch_github import fetch_github_data
from .models import UserProfile, UserStats, GitHubStats
from .forms import UserProfileForm
from .utils.fetch_leetcode import fetch_leetcode_data
from .utils.fetch_gfg import fetch_gfg_data
from collections import Counter

def home(request):
    return render(request, "index.html")
  
def extract_username(url):
    """Extracts username from a profile URL."""
    return url.rstrip("/").split("/")[-1] if url else None

def merge_heatmaps(*heatmaps):
    """Efficiently merges multiple heatmaps into one."""
    merged = Counter()
    for heatmap in heatmaps:
        merged.update(heatmap)
    return dict(merged)

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    user = request.user
    user_profile = getattr(user, 'userprofile', None)
    
    if not user_profile:
        user_profile, _ = UserProfile.objects.get_or_create(user=user)
    
    user_stats = UserStats.objects.filter(user=user_profile).first()
    github_stats = GitHubStats.objects.filter(user=user_profile).first()

    context = {
        "user": user,
        "user_stats": user_stats if user_stats else None,
        "github_stats": github_stats if github_stats else None
    }
    return render(request, "dashboard.html", context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email, password = request.POST.get("email"), request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid email or password")
    return render(request, "login.html")

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
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
    github_stats, _ = GitHubStats.objects.get_or_create(user=user_profile)

    if request.method == "POST":
        # Store old links before updating
        old_leetcode_link = user_profile.leetcode_link
        old_gfg_link = user_profile.gfg_link
        old_github_link = user_profile.github_link
        
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            # Save the updated profile links
            form.save()
            
            # Reset all stats before updating with new data
            user_stats.reset_stats()
            
            # Only fetch and update data if links are provided
            if user_profile.leetcode_link:
                leetcode_username = extract_username(user_profile.leetcode_link)
                leetcode_data = fetch_leetcode_data(leetcode_username) if leetcode_username else {}
            else:
                leetcode_data = {}
                
            if user_profile.gfg_link:
                gfg_username = extract_username(user_profile.gfg_link)
                gfg_data = fetch_gfg_data(gfg_username) if gfg_username else {}
            else:
                gfg_data = {}
            
            # Combine LeetCode and GFG data
            leetcode_easy = leetcode_data.get("difficultyCounts", {}).get("Easy", 0)
            leetcode_medium = leetcode_data.get("difficultyCounts", {}).get("Medium", 0)
            leetcode_hard = leetcode_data.get("difficultyCounts", {}).get("Hard", 0)
            leetcode_total = leetcode_data.get("difficultyCounts", {}).get("Total", 0)
            
            gfg_easy = gfg_data.get("difficultyCounts", {}).get("Easy", 0)
            gfg_medium = gfg_data.get("difficultyCounts", {}).get("Medium", 0)
            gfg_hard = gfg_data.get("difficultyCounts", {}).get("Hard", 0)
            gfg_total = gfg_data.get("difficultyCounts", {}).get("Total", 0)
            
            new_dsa_data = {
                "Easy": leetcode_easy + gfg_easy,
                "Medium": leetcode_medium + gfg_medium,
                "Hard": leetcode_hard + gfg_hard,
                "Total": leetcode_total + gfg_total,
                "Heatmap": merge_heatmaps(
                    leetcode_data.get("heatmap", {}),
                    gfg_data.get("heatmap", {})
                ),
            }
            
            # Update the user stats with the combined data
            user_stats.cumulative_stats = {
                "Easy": new_dsa_data["Easy"],
                "Medium": new_dsa_data["Medium"],
                "Hard": new_dsa_data["Hard"],
                "Total": new_dsa_data["Total"],
                "Topics": {}  # Reset topics if needed
            }
            user_stats.heatmap_data = new_dsa_data["Heatmap"]
            user_stats.total_solved = new_dsa_data["Total"]
            user_stats.update_streaks()
            user_stats.save()
            
            # Reset GitHub stats to defaults regardless
            github_stats.repo_count = 0
            github_stats.follower_count = 0
            github_stats.following_count = 0
            github_stats.total_contributions = 0
            github_stats.contribution_heatmap = {}
            
            # Only update GitHub stats if link is provided
            if user_profile.github_link:
                github_username = extract_username(user_profile.github_link)
                if github_username:
                    github_data = fetch_github_data(github_username)
                    
                    # Log GitHub data for debugging
                    logger.info(f"GitHub data fetched: {github_data}")
                    
                    # Update with new data if available and no errors
                    if github_data and not github_data.get("error"):
                        github_stats.repo_count = github_data.get("repoCount", 0)
                        github_stats.follower_count = github_data.get("followerCount", 0)
                        github_stats.following_count = github_data.get("followingCount", 0)
                        github_stats.total_contributions = github_data.get("totalContributions", 0)
                        github_stats.contribution_heatmap = github_data.get("heatmap", {})
            
            github_stats.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("dashboard")
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, "edit_profile.html", {"form": form})