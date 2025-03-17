import requests
from datetime import datetime

LEETCODE_STATS_API = "https://leetcode-stats-api.herokuapp.com/{}"

def fetch_leetcode_data(username):
    if not username:
        return {"error": "No username provided"}

    response = requests.get(LEETCODE_STATS_API.format(username))
    if response.status_code != 200:
        return {"error": "Failed to fetch LeetCode data"}

    try:
        data = response.json()
        if not data or "totalSolved" not in data:
            return {"error": "Invalid LeetCode API response"}

        # Extracting stats
        difficulty_counts = {
            "Easy": data.get("easySolved", 0),
            "Medium": data.get("mediumSolved", 0),
            "Hard": data.get("hardSolved", 0),
            "Total": data.get("totalSolved", 0),
        }

        # Extracting heatmap data
        heatmap_data = {}
        if "submissionCalendar" in data and isinstance(data["submissionCalendar"], dict):
            for timestamp, count in data["submissionCalendar"].items():
                submission_date = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
                heatmap_data[submission_date] = count

        return {
            "success": True,
            "difficultyCounts": difficulty_counts,
            "heatmap": heatmap_data,
        }

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
