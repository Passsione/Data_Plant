# YouTube Metrics Tracker

A Flask application that tracks and analyzes YouTube video metrics over time. This application allows you to monitor views, likes, comments, and subscriber counts for your favorite YouTube videos.

## Features

- Track multiple YouTube videos
- Collect metrics automatically every 24 hours
- View historical performance with interactive charts
- Easy-to-use admin interface
- RESTful API for programmatic access
- Responsive dashboard

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd youtube-metrics-tracker
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your-secret-key-here
DATABASE_URI=sqlite:///metrics.db
FLASK_APP=app.py
FLASK_ENV=development
YOUTUBE_API_KEY=your-youtube-api-key-here
```

Replace `your-youtube-api-key-here` with a valid YouTube Data API key. You can obtain one from the [Google Cloud Console](https://console.cloud.google.com/).

### 4. Initialize the database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Run the application

```bash
flask run
```

The application will be available at `http://localhost:5000`.

## Directory Structure

```
├── app.py              # Application entry point
├── models.py           # Database models
├── routes.py           # Route definitions
├── youtube_api.py      # YouTube API interactions
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Home page
│   ├── admin.html      # Admin dashboard
│   ├── add_video.html  # Add video form
│   ├── dashboard.html  # Video dashboard
│   └── video_dashboard.html  # Individual video stats
├── instance/           # Instance-specific files
│   └── metrics.db      # SQLite database
├── migrations/         # Database migrations
├── .env                # Environment variables
└── requirements.txt    # Python dependencies
```

## API Endpoints

- `GET /api/videos`: List all tracked videos
- `POST /api/videos`: Add a new video to track
- `GET /api/videos/{video_id}/stats`: Get statistics for a specific video
- `DELETE /api/videos/{video_id}`: Stop tracking a video

## Deployment

This application can be deployed to various platforms like Heroku, Vercel, or any server that supports Python applications. Make sure to set the environment variables accordingly.

For Vercel deployment, a `vercel.json` file is included for configuration.

## License

[MIT License](LICENSE)