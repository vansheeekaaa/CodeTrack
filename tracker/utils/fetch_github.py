import os
import requests

def fetch_github_data(username):
    # Load GitHub token from environment variable
    token = os.getenv("GITHUB_TOKEN")
        
    if not token:
        return {"error": "GitHub token not found. Please set the token in the environment."}

    # Set the GraphQL API endpoint
    url = "https://api.github.com/graphql"
    
    # GraphQL query to fetch data
    query = """
    query($userName: String!) {
      user(login: $userName) {
        repositories(first: 100) {
          totalCount
        }
        followers {
          totalCount
        }
        following {
          totalCount
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    
    # GraphQL variables
    variables = {"userName": username}

    # Set the request headers with the token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Make the POST request to GitHub GraphQL API
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

        # Check if response is successful
        if response.status_code == 200:
            data = response.json()
            user_data = data["data"]["user"]

            # Get counts for repositories, followers, and following
            repo_count = user_data["repositories"]["totalCount"]
            follower_count = user_data["followers"]["totalCount"]
            following_count = user_data["following"]["totalCount"]

            # Extract contribution heatmap data
            contributions = {}
            total_contributions = user_data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
            weeks = user_data["contributionsCollection"]["contributionCalendar"]["weeks"]

            for week in weeks:
                for day in week["contributionDays"]:
                    date = day["date"]
                    contribution_count = day["contributionCount"]
                    if contribution_count > 0:
                        contributions[date] = contribution_count

            return {
                "repoCount": repo_count,
                "followerCount": follower_count,
                "followingCount": following_count,
                "heatmap": contributions,
                "totalContributions": total_contributions
            }
        else:
            return {"error": "Failed to fetch data from GitHub GraphQL API. Please check the username or token."}
    except Exception as e:
        return {"error": f"Error fetching data: {str(e)}"}