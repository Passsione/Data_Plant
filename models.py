from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# This will be initialized in app.py
from app import db


class Video(db.Model):
    __tablename__ = 'Video_Base'

    # Static variables
    id = db.Column(db.String(100), primary_key=True) # url
    channel = db.Column(db.String(200)) # channel id
    created_at = db.Column(db.DateTime, default=datetime.now())
    published = db.Column(db.DateTime, default=datetime.now())
    thumbnail = db.Column(db.String(200))

    # 'Slow Moving' variables
    duration = db.Column(db.BigInteger)
    title = db.Column(db.String(150))
    description = db.Column(db.Text)
    thumbnail_width = db.Column(db.Integer)
    thumbnail_hight = db.Column(db.Integer)
    channel_title = db.Column(db.String(200))

    stats = db.relationship('VideoStats', backref='video', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'channel': self.channel,
            'channel_title': self.channel_title,
            'published': self.published.isoformat() if self.published else None,
            'thumbnail': self.thumbnail,
            'duration': self.duration,
            'description': self.description
    }
    def get_latest_stats(self):
        latest = self.stats.order_by(VideoStats.timestamp.desc()).first()
        return latest.to_dict() if latest else {}

class VideoStats(db.Model):  # Updates
    __tablename__ = 'Video_Updates'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(100), db.ForeignKey('Video_Base.id', ondelete="CASCADE"))
    timestamp = db.Column(db.DateTime, default=datetime.now()) # date the update
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    subscribers = db.Column(db.Integer, default=0)
       
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'views': self.views,
            'likes': self.likes,
            'comments': self.comments,
            'subscribers': self.subscribers
        }

# class Search(db.Model):  
# class ContentRating(db.Model): # Age-restriction
