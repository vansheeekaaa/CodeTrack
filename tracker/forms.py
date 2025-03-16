import re
from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['leetcode_link', 'gfg_link', 'code360_link', 'github_link', 'linkedin_link', 'twitter_link', 'portfolio_link']

    def _validate_profile(self, link, platform, regex):
        """Validates if a given profile link follows the correct pattern."""
        if link:
            if not re.match(regex, link):
                raise forms.ValidationError(f"Enter a valid {platform} profile link.")
        return link

    def clean_leetcode_link(self):
        return self._validate_profile(self.cleaned_data.get("leetcode_link"), "LeetCode", r"^https://leetcode\.com/[\w-]+/?$")

    def clean_gfg_link(self):
        return self._validate_profile(self.cleaned_data.get("gfg_link"), "GeeksforGeeks", r"^https://www\.geeksforgeeks\.org/user/[\w-]+/?$")

    def clean_code360_link(self):
        return self._validate_profile(self.cleaned_data.get("code360_link"), "Code360", r"^https://www\.naukri\.com/code360/profile/[\w-]+/?$")

    def clean_github_link(self):
        return self._validate_profile(self.cleaned_data.get("github_link"), "GitHub", r"^https://github\.com/[\w-]+/?$")

    def clean_linkedin_link(self):
        return self._validate_profile(self.cleaned_data.get("linkedin_link"), "LinkedIn", r"^https://www\.linkedin\.com/in/[\w-]+/?$")

    def clean_twitter_link(self):
        return self._validate_profile(self.cleaned_data.get("twitter_link"), "Twitter", r"^https://twitter\.com/[\w-]+/?$")

    def clean_portfolio_link(self):
        """Ensures portfolio links start with HTTP or HTTPS."""
        link = self.cleaned_data.get("portfolio_link")
        if link and not re.match(r"^https?://", link):
            raise forms.ValidationError("Enter a valid Portfolio link starting with http:// or https://")
        return link
