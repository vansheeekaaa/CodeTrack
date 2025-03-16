import requests
import json
from datetime import datetime
from tracker.models import UserStats, UserProfile

def debug_print_structure(data, label):
    """Helper function to print data structure in a readable format."""
    print(f"\n===== DEBUG: {label} =====")
    try:
        print(json.dumps(data, indent=4))
    except TypeError:
        print(data)

def fetch_gfg_data(username):
    if not username:
        return {"error": "No username provided"}

    BASE_URL = f'https://www.geeksforgeeks.org/gfg-assets/_next/data/uzOsUDDSPOvoyjJor0I_p/user/{username}.json'
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(BASE_URL, headers=headers)
    if response.status_code != 200:
        return {"error": "Profile Not Found"}

    try:
        user_data = response.json()
        user_info = user_data["pageProps"].get("userInfo", {})
        user_submissions = user_data["pageProps"].get("userSubmissionsInfo", {})
        heatmap_data = user_data["pageProps"].get("heatMapData", {}).get("result", {})

        debug_print_structure(user_submissions, "User Submissions")

        # ✅ Extracting difficulty counts by counting problems under each difficulty key
        difficulty_counts = {
            "easy": len(user_submissions.get("Easy", {})),  
            "medium": len(user_submissions.get("Medium", {})),  
            "hard": len(user_submissions.get("Hard", {})),  
        }

        streak_info = {
            "currentStreak": user_info.get("currentStreak", 0),
            "maxStreak": user_info.get("maxStreak", 0),
        }

        formatted_heatmap = {
            datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d"): count
            for timestamp, count in heatmap_data.items()
            if timestamp.isdigit()
        }

        debug_print_structure(formatted_heatmap, "Formatted Heatmap Data")

        user_profile = UserProfile.objects.filter(user__username=username).first()
        if not user_profile:
            return {
                "warning": "User profile not found in the database. Returning fetched data without saving.",
                "totalProblemsSolved": user_info.get("total_problems_solved", 0),
                "difficultyCounts": difficulty_counts,
                "heatmap": formatted_heatmap,
                "streakInfo": streak_info
            }

        user_stats, created = UserStats.objects.get_or_create(user=user_profile)
        user_stats.cumulative_stats["easy"] = difficulty_counts["easy"]
        user_stats.cumulative_stats["medium"] = difficulty_counts["medium"]
        user_stats.cumulative_stats["hard"] = difficulty_counts["hard"]
        user_stats.total_solved = user_info.get("total_problems_solved", 0)

        for date, count in formatted_heatmap.items():
            user_stats.heatmap_data[date] = user_stats.heatmap_data.get(date, 0) + count

        user_stats.current_streak = streak_info["currentStreak"]
        user_stats.max_streak = max(user_stats.max_streak, streak_info["maxStreak"])
        user_stats.save()

        return {
            "success": "Data successfully updated for the user",
            "totalProblemsSolved": user_stats.total_solved,
            "difficultyCounts": user_stats.cumulative_stats,
            "heatmap": user_stats.heatmap_data,
            "streakInfo": {
                "currentStreak": user_stats.current_streak,
                "maxStreak": user_stats.max_streak
            }
        }

    except (KeyError, requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Failed to parse user data. Error: {str(e)}"}
