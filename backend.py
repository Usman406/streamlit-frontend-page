from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import threading
from functools import wraps
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_hitter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Database Models
class URLSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    frequency = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Float, nullable=False)
    total_hits = db.Column(db.Integer, default=0)
    successful_hits = db.Column(db.Integer, default=0)
    failed_hits = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.now)
    end_time = db.Column(db.DateTime)
    avg_response_time = db.Column(db.Float, default=0.0)
    avg_response_size = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    hits = db.relationship('HitRecord', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'frequency': self.frequency,
            'duration': self.duration,
            'total_hits': self.total_hits,
            'successful_hits': self.successful_hits,
            'failed_hits': self.failed_hits,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'avg_response_time': round(self.avg_response_time, 2),
            'avg_response_size': round(self.avg_response_size, 2),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class HitRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('url_session.id'), nullable=False)
    hit_number = db.Column(db.Integer, nullable=False)
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float, nullable=False)
    response_size = db.Column(db.Integer, default=0)
    error_message = db.Column(db.String(500))
    hit_time = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'hit_number': self.hit_number,
            'status_code': self.status_code,
            'response_time': round(self.response_time, 3),
            'response_size': self.response_size,
            'error_message': self.error_message,
            'hit_time': self.hit_time.isoformat() if self.hit_time else None
        }

# Initialize database
with app.app_context():
    db.create_all()

# Utility function to perform URL hitting
def hit_url(session_id, url, frequency, duration, timeout=5):
    """Background task to hit URL and store results"""
    session = URLSession.query.get(session_id)
    if not session:
        return
    
    session.status = 'running'
    db.session.commit()
    
    try:
        start_time = time.time()
        interval = 1.0 / frequency
        hits = 0
        successful_hits = 0
        failed_hits = 0
        total_response_time = 0
        response_sizes = []
        
        while (time.time() - start_time) < duration:
            try:
                request_start = time.time()
                response = requests.get(url, timeout=timeout)
                response_time = time.time() - request_start
                
                hits += 1
                successful_hits += 1
                total_response_time += response_time
                response_size = len(response.content)
                response_sizes.append(response_size)
                
                # Store hit record
                hit = HitRecord(
                    session_id=session_id,
                    hit_number=hits,
                    status_code=response.status_code,
                    response_time=response_time,
                    response_size=response_size,
                    error_message=None
                )
                db.session.add(hit)
                
            except requests.exceptions.Timeout:
                hits += 1
                failed_hits += 1
                hit = HitRecord(
                    session_id=session_id,
                    hit_number=hits,
                    status_code=None,
                    response_time=0,
                    response_size=0,
                    error_message='Request timeout'
                )
                db.session.add(hit)
            except requests.exceptions.RequestException as e:
                hits += 1
                failed_hits += 1
                hit = HitRecord(
                    session_id=session_id,
                    hit_number=hits,
                    status_code=None,
                    response_time=0,
                    response_size=0,
                    error_message=str(e)
                )
                db.session.add(hit)
            
            db.session.commit()
            time.sleep(interval)
        
        # Update session with final stats
        session.total_hits = hits
        session.successful_hits = successful_hits
        session.failed_hits = failed_hits
        session.end_time = datetime.now()
        session.avg_response_time = total_response_time / successful_hits if successful_hits > 0 else 0
        session.avg_response_size = sum(response_sizes) / len(response_sizes) if response_sizes else 0
        session.status = 'completed'
        
        db.session.commit()
        
    except Exception as e:
        session.status = 'failed'
        session.end_time = datetime.now()
        db.session.commit()

# API Routes
@app.route('/api/start-hitting', methods=['POST'])
def start_hitting():
    """Start a new URL hitting session"""
    data = request.get_json()
    
    # Validate input
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data.get('url')
    frequency = data.get('frequency', 1.0)
    duration = data.get('duration', 10.0)
    timeout = data.get('timeout', 5.0)
    
    try:
        # Create session
        session = URLSession(
            url=url,
            frequency=frequency,
            duration=duration,
            status='pending'
        )
        db.session.add(session)
        db.session.commit()
        
        # Start background thread
        thread = threading.Thread(
            target=hit_url,
            args=(session.id, url, frequency, duration, timeout),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'message': 'Session started',
            'session_id': session.id,
            'status': 'pending'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details and stats"""
    session = URLSession.query.get(session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(session.to_dict()), 200

@app.route('/api/hits/<int:session_id>', methods=['GET'])
def get_hits(session_id):
    """Get all hit records for a session"""
    session = URLSession.query.get(session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Pagination support
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    hits = HitRecord.query.filter_by(session_id=session_id).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'total': hits.total,
        'pages': hits.pages,
        'current_page': page,
        'per_page': per_page,
        'hits': [hit.to_dict() for hit in hits.items]
    }), 200

@app.route('/api/sessions', methods=['GET'])
def get_all_sessions():
    """Get all sessions with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    sessions = URLSession.query.order_by(URLSession.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'total': sessions.total,
        'pages': sessions.pages,
        'current_page': page,
        'per_page': per_page,
        'sessions': [session.to_dict() for session in sessions.items]
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    total_sessions = URLSession.query.count()
    completed_sessions = URLSession.query.filter_by(status='completed').count()
    failed_sessions = URLSession.query.filter_by(status='failed').count()
    
    total_hits = db.session.query(db.func.sum(URLSession.total_hits)).scalar() or 0
    total_successful = db.session.query(db.func.sum(URLSession.successful_hits)).scalar() or 0
    
    avg_response = db.session.query(db.func.avg(URLSession.avg_response_time)).scalar() or 0
    
    return jsonify({
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'failed_sessions': failed_sessions,
        'running_sessions': total_sessions - completed_sessions - failed_sessions,
        'total_hits': total_hits,
        'total_successful': total_successful,
        'average_response_time': round(avg_response, 3)
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Backend API server starting...")
    print("📊 Database initialized at: url_hitter.db")
    print("🔗 API endpoints available at: http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  POST   /api/start-hitting       - Start new URL hitting session")
    print("  GET    /api/session/<id>        - Get session details")
    print("  GET    /api/hits/<id>           - Get hit records for session")
    print("  GET    /api/sessions            - Get all sessions")
    print("  GET    /api/stats               - Get overall statistics")
    print("  GET    /api/health              - Health check")
    print("\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
