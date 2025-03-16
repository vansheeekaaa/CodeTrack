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
    if not url:
        return None
    return url.rstrip("/").split("/")[-1]  # Get the last part of the URL

@login_required
def dashboard(request):
    user = request.user
    
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return redirect('edit_profile')  # If profile doesn't exist, redirect to edit_profile
    
    user_stats, created = UserStats.objects.get_or_create(user=profile)

    leetcode_username = extract_username(profile.leetcode_link)
    gfg_username = extract_username(profile.gfg_link)
    github_username = extract_username(profile.github_link)

    leetcode_stats = None
    gfg_stats = None
    github_stats = None
    messages_list = []

    if request.method == "POST":  # When "Refresh" is clicked
        if leetcode_username:
            leetcode_stats = fetch_leetcode_data(leetcode_username)
            if leetcode_stats:
                user_stats.update_cumulative_stats("Easy", leetcode_stats["difficultyCounts"].get("easy", 0))
                user_stats.update_cumulative_stats("Medium", leetcode_stats["difficultyCounts"].get("medium", 0))
                user_stats.update_cumulative_stats("Hard", leetcode_stats["difficultyCounts"].get("hard", 0))
                user_stats.update_total_solved()
                messages_list.append("✅ LeetCode data updated!")
            else:
                messages_list.append("⚠️ Error fetching LeetCode data or no data found.")

        if gfg_username:
            gfg_stats = fetch_gfg_data(gfg_username)  # Call your scraper
            print("GFG Stats Fetched:", gfg_stats)  # Debugging log
            if gfg_stats and "error" not in gfg_stats:
                difficulty_counts = gfg_stats.get("difficultyCounts", {"easy": 0, "medium": 0, "hard": 0})
                
                user_stats.update_cumulative_stats("Easy", difficulty_counts["easy"])
                user_stats.update_cumulative_stats("Medium", difficulty_counts["medium"])
                user_stats.update_cumulative_stats("Hard", difficulty_counts["hard"])
                
                if "heatmap" in gfg_stats:
                    user_stats.update_heatmap(gfg_stats["heatmap"])
                
                user_stats.update_total_solved()
                messages_list.append("✅ GeeksforGeeks data updated!")
            else:
                messages_list.append("⚠️ Error fetching GeeksforGeeks data or no data found.")

        if github_username:
            github_stats = fetch_github_data(github_username)
            if not github_stats or "error" in github_stats:
                messages_list.append("⚠️ Error fetching GitHub data or no data found.")
            else:
                messages_list.append("✅ GitHub data updated!")

        user_stats.save()  # Ensure stats are saved in DB

        return render(request, "dashboard.html", {
            "leetcode_stats": leetcode_stats,
            "gfg_stats": gfg_stats,
            "github_stats": github_stats,
            "user_stats": user_stats,
            "messages": messages_list if messages_list else ["✅ Data refreshed successfully!"]
        })

    return render(request, "dashboard.html", {
        "leetcode_stats": leetcode_stats,
        "gfg_stats": gfg_stats,
        "github_stats": github_stats,
        "user_stats": user_stats,
    })

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid email or password")
    return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
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
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_stats, created = UserStats.objects.get_or_create(user=user_profile)  # Ensure stats exist

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()  # Save profile links

            # Extract usernames from links
            leetcode_username = extract_username(user_profile.leetcode_link)
            gfg_username = extract_username(user_profile.gfg_link)

            # Fetch LeetCode Data
            if leetcode_username:
                leetcode_stats = fetch_leetcode_data(leetcode_username)
                if leetcode_stats:
                    user_stats.update_cumulative_stats("Easy", leetcode_stats["difficultyCounts"].get("easy", 0))
                    user_stats.update_cumulative_stats("Medium", leetcode_stats["difficultyCounts"].get("medium", 0))
                    user_stats.update_cumulative_stats("Hard", leetcode_stats["difficultyCounts"].get("hard", 0))
                    user_stats.update_total_solved()
                    messages.success(request, "✅ LeetCode data updated!")

            # Fetch GFG Data
            if gfg_username:
                gfg_stats = fetch_gfg_data(gfg_username)
                print("GFG Stats Fetched:", gfg_stats)  # Debugging log

                if gfg_stats and "error" not in gfg_stats:
                    difficulty_counts = gfg_stats.get("difficultyCounts", {"easy": 0, "medium": 0, "hard": 0})

                user_stats.update_cumulative_stats("Easy", difficulty_counts["easy"])
                user_stats.update_cumulative_stats("Medium", difficulty_counts["medium"])
                user_stats.update_cumulative_stats("Hard", difficulty_counts["hard"])

                if "heatmap" in gfg_stats:
                    user_stats.update_heatmap(gfg_stats["heatmap"])

                user_stats.update_total_solved()
                messages.success(request, "✅ GeeksforGeeks data updated!")


            user_stats.save()  # Ensure stats are saved in DB

            return redirect("dashboard")  # Redirect to dashboard after fetching data

    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, "edit_profile.html", {"form": form})
