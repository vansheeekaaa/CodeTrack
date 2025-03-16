import requests

def fetch_github_data(username):
    base_url = f"https://api.github.com/users/{username}"

    # Making requests to GitHub API
    repos_url = f"{base_url}/repos"
    followers_url = f"{base_url}/followers"
    following_url = f"{base_url}/following"

    try:
        repos_response = requests.get(repos_url)
        followers_response = requests.get(followers_url)
        following_response = requests.get(following_url)

        # Check if responses are successful
        if repos_response.status_code == 200 and followers_response.status_code == 200 and following_response.status_code == 200:
            # Get the counts from the JSON response
            repo_count = len(repos_response.json())
            follower_count = len(followers_response.json())
            following_count = len(following_response.json())

            # Return stats in a dictionary
            return {
                "repoCount": repo_count,
                "followerCount": follower_count,
                "followingCount": following_count
            }
        else:
            return {"error": "Failed to fetch GitHub stats. Please check the username."}
    except Exception as e:
        return {"error": f"Error fetching data: {str(e)}"}
