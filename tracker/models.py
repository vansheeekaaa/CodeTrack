from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

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

class UserStats(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    cumulative_stats = models.JSONField(default=default_cumulative_stats)
    heatmap_data = models.JSONField(default=default_heatmap_data)

    total_solved = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.user.user.username}"

    def update_streaks(self):
        """Updates the current streak and max streak based on heatmap_data."""
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
                current_streak = 1  # Reset streak
            else:
                current_streak = 1

            prev_date = dt

        # Ensure today's activity counts in streaks
        if today.strftime("%Y-%m-%d") in self.heatmap_data:
            current_streak += 1

        self.current_streak = current_streak
        self.max_streak = max(max_streak, current_streak)
        self.save()

    def update_total_solved(self):
        """Updates the total solved questions based on cumulative_stats."""
        self.total_solved = self.cumulative_stats.get("Total", 0)
        self.save()

    def update_heatmap(self, submission_date, count):
        """Merges heatmap data instead of replacing it."""
        self.heatmap_data[submission_date] = self.heatmap_data.get(submission_date, 0) + count
        self.save()

    def update_cumulative_stats(self, stats):
        """
        Updates cumulative stats with new values.
        stats = {"Easy": x, "Medium": y, "Hard": z, "Total": t, "Topics": {...}}
        """
        for key in ["Easy", "Medium", "Hard", "Total"]:
            if key in stats:
                self.cumulative_stats[key] = self.cumulative_stats.get(key, 0) + stats[key]

        # Updating topics
        if "Topics" in stats:
            for topic, count in stats["Topics"].items():
                self.cumulative_stats["Topics"][topic] = self.cumulative_stats["Topics"].get(topic, 0) + count

        self.save()
