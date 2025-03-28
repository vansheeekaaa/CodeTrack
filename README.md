# CodeTrack

CodeTrack is a coding activity tracker that aggregates and visualizes a user's progress across multiple coding platforms. It helps users monitor their coding streaks, track solved problems, and analyze their learning patterns through an interactive dashboard.

## Features
- **Dynamic Profile Management:** Allows users to add, update, or remove platform links, automatically refreshing stats.
- **Platform Integration:** Fetches and aggregates data from LeetCode, GeeksforGeeks, and GitHub.
- **Activity Heatmap:** Visualizes coding activity over time to track consistency.
- **Cumulative Stats:** Displays total questions solved, categorized by difficulty.

## Tech Stack
- **Backend:** Django, Python
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite3
- **APIs:** Custom API calls to fetch user data from coding platforms

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Django

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/vansheeekaaa/CodeTrack.git
   cd CodeTrack
   ```
   
2. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Start the development server:
   ```bash
   python manage.py runserver
   ```
6. Open `http://127.0.0.1:8000/` in your browser.

## Usage
- **Sign up/Login** to create your profile.
- **Add your coding platform links** (LeetCode, GeeksforGeeks, GitHub).
- **Click Refresh** to fetch and update coding stats.
- **View your dashboard** to analyze coding activity.

## Future Scope

- **More Platform Integrations:** Support for additional coding platforms like CodeChef, CodeForces, and HackerRank.

- **Competitive Programming Analysis:** Track participation and performance in contests.

- **Advanced Visualizations:** Graphical insights into topic-wise difficulty breakdown. 
