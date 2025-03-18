import requests
from datetime import datetime

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

GRAPHQL_QUERY = {
    "query": """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        username
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
        submissionCalendar
      }
    }
    """,
    "variables": {}
}

def fetch_leetcode_data(username):
    if not username:
        return {"error": "No username provided"}
    
    GRAPHQL_QUERY["variables"] = {"username": username}
    response = requests.post(LEETCODE_GRAPHQL_URL, json=GRAPHQL_QUERY)
    
    if response.status_code != 200:
        return {"error": "Failed to fetch LeetCode data"}
    
    try:
        data = response.json()
        user_data = data.get("data", {}).get("matchedUser", {})
        
        if not user_data:
            return {"error": "Invalid LeetCode username or API response"}
        
        submissions = user_data.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
        difficulty_counts = {difficulty["difficulty"]: difficulty["count"] for difficulty in submissions}
        
        # Ensure we have default values
        difficulty_counts = {
            "Easy": difficulty_counts.get("Easy", 0),
            "Medium": difficulty_counts.get("Medium", 0),
            "Hard": difficulty_counts.get("Hard", 0),
            "Total": difficulty_counts.get("All", 0),
        }
        
        # Extract heatmap data
        heatmap_data = {}
        submission_calendar = user_data.get("submissionCalendar", {})
        if isinstance(submission_calendar, str):
            import json
            submission_calendar = json.loads(submission_calendar)
        
        if isinstance(submission_calendar, dict):
            for timestamp, count in submission_calendar.items():
                submission_date = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d")
                heatmap_data[submission_date] = count
        
        return {
            "success": True,
            "difficultyCounts": difficulty_counts,
            "heatmap": heatmap_data
        }
    
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
