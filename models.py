from datetime import datetime
from app import db

class Video(db.Model):
    __tablename__ = 'Video_Base'

    # Static variables
    id = db.Column(db.String(100), primary_key=True) # url
    channel = db.Column(db.String(200)) # channel id
    created_at = db.Column(db.DateTime, default=datetime.now())
    published = db.Column(db.DateTime, default=datetime.now())
    thumbnail = db.Column(db.String(100))

    # 'Slow Moving' variables
    duration = db.Column(db.BigInteger)
    title = db.Column(db.String(100))
    description = db.Column(db.String)
    thumbnail_width = db.Column(db.Integer)
    thumbnail_hight = db.Column(db.Integer)
    channel_title = db.Column(db.String(200))

    stats = db.relationship('VideoStats', backref='video', lazy='dynamic')
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'channel': self.channel_title,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'thumbnail': self.thumbnail,
            'duration': self.duration
    }
class VideoStats(db.Model):  # Updates
    __tablename__ = 'Video_Updates'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(50), db.ForeignKey('Video_Base.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now()) # date the update
    views = db.Column(db.BigInteger)
    likes = db.Column(db.BigInteger)
    comments = db.Column(db.BigInteger)
    subscribers = db.Column(db.BigInteger)
       
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
