from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default-secret-key-for-dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI", 'sqlite:///metrics.db')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SCHEDULER_API_ENABLED"] = True

  # Import extensions after creating app but before initializing
    from extensions import db, migrate, scheduler


    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models after db is defined
    from models import Video, VideoStats
    
    # Register routes
    from routes import register_routes
    register_routes(app)
    
    # Initialize scheduler
    if not scheduler.running:
        scheduler.start()
        from youtube_api import update_video_stats
        
        scheduler.add_job(
            id='Scheduled Stats Update',
            func=update_video_stats,
            trigger='interval',
            hours=24,
            args=[app]
        )
    
    return app
app = create_app()
if __name__ == '__main__':
    with app.app_context():
        from extensions import db
        db.create_all()
    app.run(debug=True)
