# 🚀 Advanced URL Hitter - Full Stack Application

Pakistan-themed **Streamlit Frontend** + **Flask Backend API** application for hitting URLs with advanced analytics.

## 📋 Features

### Frontend (Streamlit)
- 🎨 Dark theme with Pakistan flag colors
- 🏔️ Hunza Valley background image
- 📊 Real-time statistics and progress tracking
- 📝 Detailed hit logs with response times
- 🇵🇰 Pakistan-themed UI elements

### Backend (Flask API)
- ✅ RESTful API for URL hitting sessions
- 💾 SQLite database for data persistence
- 🔄 Background threading for concurrent requests
- 📈 Session management and analytics
- 🏥 Health check endpoints

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone/Extract the project**
```bash
cd api\ shudalerr
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize database** (automatic on first backend run)

## 🚀 Running the Application

### Option 1: Run Both (Recommended)

**Terminal 1 - Start Backend API**
```bash
python backend.py
```
Backend will run at: `http://localhost:5000`

**Terminal 2 - Start Frontend**
```bash
streamlit run frontend.py
```
Frontend will run at: `http://localhost:8501`

### Option 2: Frontend Only (Direct Mode)
```bash
streamlit run frontend.py
```
The frontend works standalone with direct requests.

## 📡 API Endpoints

### Start URL Hitting Session
```
POST /api/start-hitting
```
**Request:**
```json
{
    "url": "https://example.com",
    "frequency": 5.0,
    "duration": 60.0,
    "timeout": 5.0
}
```
**Response:**
```json
{
    "message": "Session started",
    "session_id": 1,
    "status": "pending"
}
```

### Get Session Details
```
GET /api/session/<session_id>
```
Returns full session statistics and metadata.

### Get Hit Records
```
GET /api/hits/<session_id>?page=1&per_page=100
```
Returns paginated hit records for a session.

### Get All Sessions
```
GET /api/sessions?page=1&per_page=20
```
Returns all sessions with pagination.

### Get Overall Statistics
```
GET /api/stats
```
Returns platform-wide statistics.

### Health Check
```
GET /api/health
```
Returns API health status.

## 📊 Database Schema

### URLSession Table
- `id` - Primary key
- `url` - Target URL
- `frequency` - Hits per second
- `duration` - Session duration (seconds)
- `total_hits` - Total requests sent
- `successful_hits` - Successful requests
- `failed_hits` - Failed requests
- `avg_response_time` - Average response time (ms)
- `avg_response_size` - Average response size (bytes)
- `status` - Session status (pending/running/completed/failed)
- `created_at` - Creation timestamp

### HitRecord Table
- `id` - Primary key
- `session_id` - Foreign key to URLSession
- `hit_number` - Sequential hit number
- `status_code` - HTTP status code
- `response_time` - Response time (ms)
- `response_size` - Response size (bytes)
- `error_message` - Error message if any
- `hit_time` - Hit timestamp

## 🎨 Customization

### Changing Colors
Edit CSS in `frontend.py` around line 20-90:
- `#CE1126` - Pakistan red
- `#1F4788` - Pakistan blue
- `#000000` - Dark theme black

### Changing Background Image
Update URL in `frontend.py` line 16:
```python
url('https://your-image-url.jpg')
```

## 📝 Usage Example

### Using Frontend
1. Open Streamlit app at `http://localhost:8501`
2. Enter frequency (hits/second) - default 1.0
3. Enter duration (seconds) - default 10.0
4. Enter target URL
5. Click "🎯 Start Hitting URL"
6. View real-time stats and detailed logs

### Using API (cURL)
```bash
# Start session
curl -X POST http://localhost:5000/api/start-hitting \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/get",
    "frequency": 2.0,
    "duration": 30.0
  }'

# Get session details
curl http://localhost:5000/api/session/1

# Get hits
curl http://localhost:5000/api/hits/1

# Get stats
curl http://localhost:5000/api/stats
```

## 🔒 Security Notes

- Backend uses CORS (Cross-Origin Resource Sharing)
- No authentication currently - add JWT for production
- Validate all inputs before processing
- Rate limiting recommended for production

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in backend.py line 318:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Corruption
```bash
# Delete and rebuild
rm url_hitter.db
python backend.py
```

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

## 📄 License

Pakistan Edition 🇵🇰 - 2025

## 👨‍💻 Developer

**Usman406** - Made with ❤️ in Pakistan 🇵🇰

---

**Hunza Valley Background** 🏔️ | **Advanced URL Hitter v2.0** 🚀
