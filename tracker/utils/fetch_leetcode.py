from datetime import datetime
import requests
from tracker.models import UserStats, UserProfile

LEETCODE_STATS_API = "https://leetcode-stats-api.herokuapp.com/{}"

def fetch_leetcode_data(username):
    if not username:
        return {"error": "No username provided"}

    # Fetch data from LeetCode Stats API
    response = requests.get(LEETCODE_STATS_API.format(username))
    if response.status_code != 200:
        return {"error": "Failed to fetch LeetCode data"}

    try:
        data = response.json()
        if not data or "totalSolved" not in data:
            return {"error": "Invalid LeetCode API response"}

        # Find the UserProfile linked to this username
        user_profile = UserProfile.objects.filter(leetcode_link__icontains=username).first()
        if not user_profile:
            return {"error": "User profile not found"}

        # Get or create UserStats for the user
        user_stats, created = UserStats.objects.get_or_create(user=user_profile)

        # Fix difficulty key mapping
        new_stats = {
            "Easy": data.get("easySolved", 0),
            "Medium": data.get("mediumSolved", 0),
            "Hard": data.get("hardSolved", 0),
            "Total": data.get("totalSolved", 0),
        }
        user_stats.update_cumulative_stats(new_stats)

        # Fix heatmap merging logic
        if "submissionCalendar" in data and isinstance(data["submissionCalendar"], dict):
            for timestamp, count in data["submissionCalendar"].items():
                submission_date = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
                user_stats.update_heatmap(submission_date, count)

        # Save user stats
        user_stats.save()

        # Ensure streaks & total solved are updated
        user_stats.update_streaks()
        user_stats.update_total_solved()

        return {"success": "LeetCode data updated"}

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
