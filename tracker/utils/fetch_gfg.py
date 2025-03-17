import requests
import json
from datetime import datetime

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

        # ✅ Extracting difficulty counts
        difficulty_counts = {
            "Easy": len(user_submissions.get("Easy", {})),  
            "Medium": len(user_submissions.get("Medium", {})),  
            "Hard": len(user_submissions.get("Hard", {})),  
            "Total": sum(len(user_submissions.get(difficulty, {})) for difficulty in ["Easy", "Medium", "Hard"])
        }

        # ✅ Extracting streak info
        streak_info = {
            "currentStreak": user_info.get("currentStreak", 0),
            "maxStreak": user_info.get("maxStreak", 0),
        }

        # ✅ Formatting heatmap data
        formatted_heatmap = {
            datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d"): count
            for timestamp, count in heatmap_data.items()
            if timestamp.isdigit()
        }

        debug_print_structure(formatted_heatmap, "Formatted Heatmap Data")

        return {
            "success": True,
            "difficultyCounts": difficulty_counts,
            "heatmap": formatted_heatmap,
            "streakInfo": streak_info
        }

    except (KeyError, requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Failed to parse user data. Error: {str(e)}"}
