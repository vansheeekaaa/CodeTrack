import requests
from datetime import datetime

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

        # ✅ Extracting difficulty counts with correct list handling
        difficulty_counts = {
            "Easy": len(user_submissions.get("easy", [])),  
            "Medium": len(user_submissions.get("medium", [])),  
            "Hard": len(user_submissions.get("hard", [])),  
            "Total": sum(len(user_submissions.get(difficulty, [])) for difficulty in ["easy", "medium", "hard"])
        }

        # ✅ Extracting streak info
        streak_info = {
            "currentStreak": user_info.get("currentStreak", 0),
            "maxStreak": user_info.get("maxStreak", 0),
        }

        # ✅ Formatting heatmap data (Only convert timestamps if needed)
        if all(k.isdigit() for k in heatmap_data.keys()):  
            formatted_heatmap = {
                datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d"): count
                for timestamp, count in heatmap_data.items()
            }
        else:
            formatted_heatmap = heatmap_data  # Already formatted, use as-is

        return {
            "success": True,
            "difficultyCounts": difficulty_counts,
            "heatmap": formatted_heatmap,
            "streakInfo": streak_info
        }

    except (KeyError, requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Failed to parse user data. Error: {str(e)}"}