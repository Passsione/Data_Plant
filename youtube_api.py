import os
import requests
from datetime import datetime, timedelta
import isodate  # type: ignore # For parsing YouTube duration format
from models import Video, VideoStats
from app import db

# Get YouTube API key from environment variables
API_KEY = os.environ.get('YOUTUBE_API_KEY')

def update_video_stats(app):
    """Function to update stats for all tracked videos"""
    with app.app_context():
        videos = Video.query.all()
        for video in videos:
            try:
                # Get latest stats from YouTube API
                stats = get_video_stats(video.id)
                if stats:
                    new_stat = VideoStats(
                        video_id=video.id,
                        views=stats.get('views', 0),
                        likes=stats.get('likes', 0),
                        comments=stats.get('comments', 0),
                        subscribers=stats.get('subscribers', 0)
                    )
                    db.session.add(new_stat)
            except Exception as e:
                print(f"Error updating stats for video {video.id}: {str(e)}")
                continue
                
        db.session.commit()
        print(f"Stats updated at {datetime.utcnow()}")

def fetch_video_details(video_id):
    """Fetch video details from YouTube API"""
    if not API_KEY:
        # For development/testing without API key
        return {
            'title': f'Test Video {video_id}',
            'description': 'This is a test video description',
            'thumbnail': f'https://img.youtube.com/vi/{video_id}/0.jpg',
            'channel_id': 'test_channel',
            'channel_title': 'Test Channel',
            'duration': 120,  # 2 minutes
            'published': datetime.utcnow() - timedelta(days=10)
        }
    
    try:
        # Make API request to YouTube Data API v3
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            'key': API_KEY,
            'id': video_id,
            'part': 'snippet,contentDetails,statistics'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'items' not in data or len(data['items']) == 0:
            return None
            
        video_data = data['items'][0]
        snippet = video_data.get('snippet', {})
        content_details = video_data.get('contentDetails', {})
        
        # Parse duration from ISO 8601 format
        duration_str = content_details.get('duration', 'PT0S')
        duration_seconds = int(isodate.parse_duration(duration_str).total_seconds())
        
        # Parse published date
        published_str = snippet.get('publishedAt')
        published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00')) if published_str else None
        
        # Get thumbnail
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = None
        for quality in ['maxres', 'high', 'medium', 'default']:
            if quality in thumbnails:
                thumbnail_url = thumbnails[quality].get('url')
                break
                
        return {
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'thumbnail': thumbnail_url,
            'channel_id': snippet.get('channelId', ''),
            'channel_title': snippet.get('channelTitle', ''),
            'duration': duration_seconds,
            'published': published_date
        }
    except Exception as e:
        print(f"Error fetching video details: {str(e)}")
        return None

def get_video_stats(video_id):
    """Get current statistics for a video"""
    if not API_KEY:
        # For development/testing without API key
        import random
        return {
            'views': random.randint(500, 10000),
            'likes': random.randint(50, 1000),
            'comments': random.randint(10, 200),
            'subscribers': random.randint(100, 5000)
        }
    
    try:
        # Make API request to YouTube Data API v3
        video_url = f"https://www.googleapis.com/youtube/v3/videos"
        video_params = {
            'key': API_KEY,
            'id': video_id,
            'part': 'statistics'
        }
        
        video_response = requests.get(video_url, params=video_params)
        video_data = video_response.json()
        
        if 'items' not in video_data or len(video_data['items']) == 0:
            return None
            
        statistics = video_data['items'][0].get('statistics', {})
        
        # Get channel ID to fetch subscriber count
        channel_url = f"https://www.googleapis.com/youtube/v3/videos"
        channel_params = {
            'key': API_KEY,
            'id': video_id,
            'part': 'snippet'
        }
        
        channel_response = requests.get(channel_url, params=channel_params)
        channel_data = channel_response.json()
        
        channel_id = None
        if 'items' in channel_data and len(channel_data['items']) > 0:
            channel_id = channel_data['items'][0].get('snippet', {}).get('channelId')
        
        subscribers = 0
        if channel_id:
            subscriber_url = f"https://www.googleapis.com/youtube/v3/channels"
            subscriber_params = {
                'key': API_KEY,
                'id': channel_id,
                'part': 'statistics'
            }
            
            subscriber_response = requests.get(subscriber_url, params=subscriber_params)
            subscriber_data = subscriber_response.json()
            
            if 'items' in subscriber_data and len(subscriber_data['items']) > 0:
                subscribers = int(subscriber_data['items'][0].get('statistics', {}).get('subscriberCount', 0))
        
        return {
            'views': int(statistics.get('viewCount', 0)),
            'likes': int(statistics.get('likeCount', 0)),
            'comments': int(statistics.get('commentCount', 0)),
            'subscribers': subscribers
        }
    except Exception as e:
        print(f"Error fetching video stats: {str(e)}")
        return None