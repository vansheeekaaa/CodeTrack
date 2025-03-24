from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Default function for cumulative_stats
def default_cumulative_stats():
    return {"Easy": 0, "Medium": 0, "Hard": 0, "Total": 0, "Topics": {}}

# Default function for heatmap_data
def default_heatmap_data():
    return {}

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leetcode_link = models.URLField(blank=True, null=True)
    gfg_link = models.URLField(blank=True, null=True)
    code360_link = models.URLField(blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    portfolio_link = models.URLField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class GitHubStats(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="github_stats")
    repo_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    total_contributions = models.IntegerField(default=0)
    contribution_heatmap = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GitHub Stats for {self.user.user.username}"

    def update_github_data(self, github_data):
        if not github_data:
            return

        self.repo_count = github_data.get("repoCount", self.repo_count)
        self.follower_count = github_data.get("followerCount", self.follower_count)
        self.following_count = github_data.get("followingCount", self.following_count)
        self.total_contributions = github_data.get("totalContributions", self.total_contributions)
        
        if "heatmap" in github_data:
            self.contribution_heatmap.update(github_data["heatmap"])
        
        self.save()

class UserStats(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    cumulative_stats = models.JSONField(default=default_cumulative_stats)
    heatmap_data = models.JSONField(default=default_heatmap_data)
    total_solved = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.user.user.username}"

    def reset_stats(self):
        self.cumulative_stats = default_cumulative_stats()
        self.heatmap_data = default_heatmap_data()
        self.total_solved = 0
        self.max_streak = 0
        self.current_streak = 0
        self.save()

    def update_streaks(self):
        dates = sorted(self.heatmap_data.keys())
        current_streak = 0
        max_streak = 0
        prev_date = None
        today = datetime.utcnow().date()

        for date in dates:
            dt = datetime.strptime(date, "%Y-%m-%d").date()
            if prev_date and (dt - prev_date).days == 1:
                current_streak += 1
            elif prev_date and (dt - prev_date).days > 1:
                max_streak = max(max_streak, current_streak)
                current_streak = 1
            else:
                current_streak = 1
            prev_date = dt

        if today.strftime("%Y-%m-%d") in self.heatmap_data:
            if prev_date is None or (today - prev_date).days <= 1:
                current_streak += 1
            else:
                max_streak = max(max_streak, current_streak)
                current_streak = 1

        self.current_streak = current_streak
        self.max_streak = max(max_streak, current_streak)
        self.save()

    def update_total_solved(self):
        self.total_solved = self.cumulative_stats.get("Total", 0)
        self.save()

    def update_heatmap(self, submission_date, count):
        self.heatmap_data[submission_date] = self.heatmap_data.get(submission_date, 0) + count
        self.save()

    def update_cumulative_stats(self, new_stats):
        for key in ["Easy", "Medium", "Hard", "Total"]:
            if key in new_stats:
                if new_stats[key] >= self.cumulative_stats.get(key, 0):
                    self.cumulative_stats[key] = new_stats[key]
                else:
                    self.cumulative_stats[key] = max(self.cumulative_stats[key], new_stats[key])

        if "Topics" in new_stats:
            if "Topics" not in self.cumulative_stats:
                self.cumulative_stats["Topics"] = {}
            for topic, count in new_stats["Topics"].items():
                self.cumulative_stats["Topics"][topic] = self.cumulative_stats["Topics"].get(topic, 0) + count

        self.save()

    def update_from_platform(self, new_data):
        if not new_data:
            return

        self.update_cumulative_stats(new_data)
        
        if "Heatmap" in new_data:
            for date, count in new_data["Heatmap"].items():
                self.update_heatmap(date, count)

        self.update_streaks()
        self.update_total_solved()
