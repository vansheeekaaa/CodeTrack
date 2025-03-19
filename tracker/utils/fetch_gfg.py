import requests
from datetime import datetime

def fetch_gfg_data(username):
    if not username:
        return {"error": "No username provided"}

    # ✅ Fetch general profile data
    BASE_URL = f'https://geeks-for-geeks-api.vercel.app/{username}'
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(BASE_URL, headers=headers)
    if response.status_code != 200:
        return {"error": "Profile Not Found"}

    try:
        user_data = response.json()
        user_info = user_data.get("info", {})

        difficulty_counts = {
            "Easy": user_data.get("solvedStats", {}).get("easy", {}).get("count", 0),
            "Medium": user_data.get("solvedStats", {}).get("medium", {}).get("count", 0),
            "Hard": user_data.get("solvedStats", {}).get("hard", {}).get("count", 0),
            "Total": user_info.get("totalProblemsSolved", 0),
        }

        streak_info = {
            "currentStreak": user_info.get("currentStreak", 0),
            "maxStreak": user_info.get("maxStreak", 0),
        }

        # ✅ Fetch submission heatmap data
        heatmap_url = "https://practiceapi.geeksforgeeks.org/api/v1/user/problems/submissions/"
        heatmap_payload = {
            "handle": username,
            "requestType": "getYearwiseUserSubmissions",
            "year": datetime.now().year,
            "month": ""  # Fetching all months of the year
        }

        heatmap_response = requests.post(heatmap_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://practice.geeksforgeeks.org/",
            "Content-Type": "application/json"
        }, json=heatmap_payload)

        heatmap_data = heatmap_response.json() if heatmap_response.status_code == 200 else {}

        return {
            "difficultyCounts": difficulty_counts,
            "streakInfo": streak_info,
            "heatmap": heatmap_data.get("result", {})  # Store submission heatmap data
        }

    except (KeyError, requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Failed to parse user data. Error: {str(e)}"}
