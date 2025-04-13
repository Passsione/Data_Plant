from flask import render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
from models import *
from extensions import db
from youtube_api import fetch_video_details, get_video_stats

def register_routes(app):
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/admin')
    def admin():
        videos = Video.query.all()
        return render_template('admin.html', videos=videos)
    
    @app.route('/admin/add', methods=['GET', 'POST'])
    def add_video_form():
        if request.method == 'POST':
            video_id = request.form.get('video_id')
            # Check if video already exists
            existing = Video.query.get(video_id)
            if existing:
                flash('Video already exists in database', 'warning')
                return redirect(url_for('admin'))
                
            # Fetch video details from YouTube API
            try:
                video_data = fetch_video_details(video_id)
                if not video_data:
                    flash('Could not fetch video data from YouTube API', 'error')
                    return redirect(url_for('add_video_form'))
                
                # Create new video object
                new_video = Video(
                    id=video_id,
                    title=video_data.get('title', 'Unknown'),
                    channel=video_data.get('channel_id', ''),
                    channel_title=video_data.get('channel_title', ''),
                    description=video_data.get('description', ''),
                    thumbnail=video_data.get('thumbnail', ''),
                    duration=video_data.get('duration', 0),
                    published=video_data.get('published')
                )
                
                # Add to database
                db.session.add(new_video)
                db.session.commit()
                
                # Fetch initial stats
                stats = get_video_stats(video_id)
                if stats:
                    new_stats = VideoStats(
                        video_id=video_id,
                        views=stats.get('views', 0),
                        likes=stats.get('likes', 0),
                        comments=stats.get('comments', 0),
                        subscribers=stats.get('subscribers', 0)
                    )
                    db.session.add(new_stats)
                    db.session.commit()
                
                flash('Video added successfully', 'success')
                return redirect(url_for('admin'))
            except Exception as e:
                flash(f'Error adding video: {str(e)}', 'error')
                return redirect(url_for('add_video_form'))
                
        return render_template('add_video.html')
    
    @app.route('/admin/delete/<video_id>', methods=['POST'])
    def delete_video(video_id):
        video = Video.query.get_or_404(video_id)
        db.session.delete(video)
        db.session.commit()
        flash('Video deleted successfully', 'success')
        return redirect(url_for('admin'))
    
    @app.route('/dashboard')
    def dashboard():
        videos = Video.query.all()
        latest_stats = []
        for video in videos:
            video_stats = video.stats.order_by(VideoStats.timestamp.desc()).first()
            latest_stats.append(video_stats)
        
        return render_template('dashboard.html', videos=videos, stats=latest_stats)
    
    @app.route('/dashboard/<video_id>')
    def video_dashboard(video_id):
        video = Video.query.get_or_404(video_id)
        stats = video.stats.order_by(VideoStats.timestamp.desc()).all()
        return render_template('video_dashboard.html', video=video, stats=stats)
    
    # API Routes
    @app.route('/api/videos', methods=['GET'])
    def get_videos():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = Video.query.paginate(page=page, per_page=per_page)
        videos = pagination.items
        
        return jsonify({
            'videos': [{
                'id': v.id,
                'title': v.title,
                'channel': v.channel_title,
                'duration': v.duration,
                'thumbnail': v.thumbnail,
                'published': v.published.isoformat() if v.published else None,
                'stats_count': v.stats.count(),
                'latest_stats': v.get_latest_stats()
            } for v in videos],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    
    @app.route('/api/videos', methods=['POST'])
    def add_video_api():
        data = request.get_json()
        if not data or 'video_id' not in data:
            return jsonify({'error': 'Missing video_id parameter'}), 400
            
        video_id = data['video_id']
        
        # Check if video already exists
        existing = Video.query.get(video_id)
        if existing:
            return jsonify({'error': 'Video already exists'}), 409
            
        # Fetch video details from YouTube API
        try:
            video_data = fetch_video_details(video_id)
            if not video_data:
                return jsonify({'error': 'Could not fetch video data from YouTube API'}), 404
                
            # Create new video object
            new_video = Video(
                id=video_id,
                title=video_data.get('title', 'Unknown'),
                channel=video_data.get('channel_id', ''),
                channel_title=video_data.get('channel_title', ''),
                description=video_data.get('description', ''),
                thumbnail=video_data.get('thumbnail', ''),
                duration=video_data.get('duration', 0),
                published=video_data.get('published')
            )
            
            # Add to database
            db.session.add(new_video)
            db.session.commit()
            
            # Fetch initial stats
            stats = get_video_stats(video_id)
            if stats:
                new_stats = VideoStats(
                    video_id=video_id,
                    views=stats.get('views', 0),
                    likes=stats.get('likes', 0),
                    comments=stats.get('comments', 0),
                    subscribers=stats.get('subscribers', 0)
                )
                db.session.add(new_stats)
                db.session.commit()
            
            return jsonify({'message': 'Video added successfully', 'video': new_video.to_dict()}), 201
        except Exception as e:
            return jsonify({'error': f'Error adding video: {str(e)}'}), 500
    
    @app.route('/api/videos/<video_id>/stats', methods=['GET'])
    def get_video_stats_api(video_id):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = VideoStats.query.filter_by(video_id=video_id)
        
        if start_date:
            query = query.filter(VideoStats.timestamp >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(VideoStats.timestamp <= datetime.fromisoformat(end_date))
        
        stats = query.order_by(VideoStats.timestamp.asc()).all()
        return jsonify([s.to_dict() for s in stats])
    
    @app.route('/api/videos/<video_id>', methods=['DELETE'])
    def delete_video_api(video_id):
        video = Video.query.get_or_404(video_id)
        db.session.delete(video)
        db.session.commit()
        return jsonify({'message': 'Video deleted successfully'})