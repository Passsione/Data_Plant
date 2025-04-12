from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv
from models import *
from datetime import datetime


load_dotenv()
db = SQLAlchemy()
migrate = Migrate()
scheduler = BackgroundScheduler()


app = Flask(__name__)
app.config["SECRET_KEY"] = "AIzaSyCgUAA4iv3g487CITmxRvzbNYvnJlc_IiU"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///metrics.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SCHEDULER_API_ENABLED"] = True


# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# Initialize scheduler
if not scheduler.running:
    scheduler.start()
    from func import * 

    scheduler.add_job(
        id='Scheduled Stats Update',
        func=update_video_stats,
        trigger='interval',
        hours=24,
        args=[app]
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/videos', methods=['POST'])
def add_video():
    data = request.get_json()
    video = Video(
        id=data['video_id'],
        title=data['title'],
        channel=data['channel'],
        duration=data.get('duration', 0),
        description=data.get('description', ''),
        thumbnail=data.get('thumbnail', ''),
        channel_title=data.get('channel_title', '')
    )
    db.session.add(video)
    db.session.commit()
    return jsonify({'message': 'Video added successfully'}), 201

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
            'stats_count': v.stats.count()
        } for v in videos],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })

@app.route('/api/videos/<video_id>/stats', methods=['GET'])
def get_video_stats(video_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = VideoStats.query.filter_by(video_id=video_id)
    
    if start_date:
        query = query.filter(VideoStats.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(VideoStats.timestamp <= datetime.fromisoformat(end_date))
    
    stats = query.order_by(VideoStats.timestamp.asc()).all()
    return jsonify([s.to_dict() for s in stats])
    """Stop tracking a video and delete its data"""
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    return jsonify({'message': 'Video deleted successfully'})

# Add this to existing routes
@app.route('/dashboard')
def dashboard():
    """Simple HTML dashboard"""
    videos = Video.query.all()
    return '''
    <html>
        <head><title>YouTube Metrics Dashboard</title></head>
        <body>
            <h1>Tracked Videos</h1>
            <ul>
                {% for video in videos %}
                <li>
                    <a href="/dashboard/{{ video.id }}">{{ video.title }}</a>
                    ({{ video.channel }})
                </li>
                {% endfor %}
            </ul>
        </body>
    </html>
    ''', 200

@app.route('/dashboard/<video_id>')
def video_dashboard(video_id):
    """Video-specific dashboard with charts"""
    video = Video.query.get_or_404(video_id)
    stats = video.stats.order_by(VideoStats.timestamp.asc()).all()
    
    # Simple chart using Chart.js
    return f'''
    <html>
        <head>
            <title>{video.title} Stats</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h1>{video.title}</h1>
            <canvas id="statsChart" width="800" height="400"></canvas>
            <script>
                const ctx = document.getElementById('statsChart');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {[s.timestamp.strftime('%Y-%m-%d') for s in stats]},
                        datasets: [
                            {{
                                label: 'Views',
                                data: {[s.views for s in stats]},
                                borderColor: 'rgb(255, 99, 132)'
                            }},
                            {{
                                label: 'Likes',
                                data: {[s.likes for s in stats]},
                                borderColor: 'rgb(54, 162, 235)'
                            }}
                        ]
                    }}
                }});
            </script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)