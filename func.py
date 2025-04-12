from models import *
from datetime import datetime


def update_video_stats(app):
    with app.app_context():
        videos = Video.query.all()
        for video in videos:
            # Replace with actual YouTube API call
            stats = get_video_stats_YT(video.id)
            
            new_stat = VideoStats(
                video_id=video.id,
                views=stats['views'],
                likes=stats['likes'],
                comments=stats['comments'],
                subscribers=stats['subscribers']
            )
            db.session.add(new_stat)

            
        db.session.commit()

def get_video_stats_YT(video_id):
    # Implement actual YouTube API call here
    return {
        'views': 1000,
        'likes': 50,
        'comments': 20,
        'subscribers': 500
    }
