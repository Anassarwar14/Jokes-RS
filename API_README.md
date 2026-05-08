# Jokes Recommendation API Backend

FastAPI backend for the Jokes Recommendation System. Exposes trained PMF and autoencoder models via REST endpoints for frontend consumption.

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (or use Docker Compose)
- Virtual environment activated

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start PostgreSQL
```bash
docker-compose up -d
```

### 3. Initialize Database
```bash
python -c "from api.database import init_db; init_db()"
```

### 4. Run the API Server
```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

- **API Docs (Swagger UI)**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

---

## API Endpoints

### Sessions
Create and manage user sessions for recommendations.

#### Create Session
```http
POST /api/sessions
```
Creates a new ephemeral session with auto-assigned user ID.

**Request:**
```json
{}
```

**Response (201 Created):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 123456,
  "created_at": "2024-05-06T12:00:00",
  "last_active_at": "2024-05-06T12:00:00",
  "is_active": true
}
```

#### Get Session
```http
GET /api/sessions/{session_id}
```

#### Validate Session
```http
POST /api/sessions/{session_id}/validate
```

---

### Ratings
Submit and retrieve user ratings.

#### Submit Rating
```http
POST /api/ratings
```

**Request:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 123456,
  "joke_id": 42,
  "rating": 7.5
}
```

Rating scale: -10 to 10 (Jester dataset format)

**Response (201 Created):**
```json
{
  "user_id": 123456,
  "joke_id": 42,
  "rating": 7.5,
  "created_at": "2024-05-06T12:01:00",
  "updated_at": "2024-05-06T12:01:00"
}
```

#### Get User Rating
```http
GET /api/ratings/{user_id}/{joke_id}
```

#### Get All User Ratings
```http
GET /api/ratings/{user_id}
```

**Response:**
```json
{
  "user_id": 123456,
  "ratings": [
    {"user_id": 123456, "joke_id": 1, "rating": 5.0, "created_at": "...", "updated_at": "..."},
    {"user_id": 123456, "joke_id": 42, "rating": 7.5, "created_at": "...", "updated_at": "..."}
  ]
}
```

---

### Recommendations
Get personalized recommendations.

#### Get Recommendations
```http
GET /api/recommendations/{user_id}?model=pmf&top_k=10
```

**Query Parameters:**
- `model` (string): `pmf` or `autoencoder` (default: `pmf`)
- `top_k` (integer): Number of recommendations, 1-100 (default: 10)

**Response:**
```json
{
  "user_id": 123456,
  "model": "pmf",
  "top_k": 10,
  "recommendations": [
    {
      "joke_id": 5,
      "joke_text": "A man visits the doctor. The doctor says ...",
      "predicted_rating": 8.2,
      "rank": 1
    },
    {
      "joke_id": 12,
      "joke_text": "What's the difference between ...",
      "predicted_rating": 7.9,
      "rank": 2
    },
    {
      "joke_id": 8,
      "joke_text": "What's 200 feet long ...",
      "predicted_rating": 7.6,
      "rank": 3
    }
  ],
  "generated_at": "2024-05-06T12:02:00"
}
```

**Example with Autoencoder:**
```http
GET /api/recommendations/123456?model=autoencoder&top_k=5
```

---

### Joke Catalog
The backend exposes joke text via the joke catalog endpoints.

#### List Jokes
```http
GET /api/jokes?limit=50
```

#### Get Joke by ID
```http
GET /api/jokes/{joke_id}
```

**Response:**
```json
{
  "joke_id": 5,
  "joke_text": "A man visits the doctor. The doctor says ..."
}
```

---

### Models
Information about available models.

#### List All Models
```http
GET /api/models
```

**Response:**
```json
{
  "models": [
    {
      "model_type": "pmf",
      "model_name": "pmf_k10_sigmaU0.1_sigmaV0.1_bs1000",
      "model_path": "/path/to/models/pmf/pmf_k10_sigmaU0.1_sigmaV0.1_bs1000.npz",
      "metrics": {
        "test_rmse": 3.45,
        "test_mae": 2.1,
        "test_ndcg_10": 0.52,
        "test_recall_10": 0.38
      }
    },
    {
      "model_type": "autoencoder",
      "model_name": "best_model",
      "model_path": "/path/to/models/autoencoder/best_model.pt",
      "metrics": {...}
    }
  ],
  "default_model": "pmf"
}
```

#### List Models by Type
```http
GET /api/models/pmf
```

#### Get Specific Model Info
```http
GET /api/models/pmf/pmf_k10_sigmaU0.1_sigmaV0.1_bs1000
```

---

## Workflow Example

### 1. Create a Session
```bash
curl -X POST http://localhost:8000/api/sessions
```

Response:
```json
{"session_id": "abc123", "user_id": 456789, ...}
```

### 2. Get Initial Recommendations (Cold Start)
```bash
curl http://localhost:8000/api/recommendations/456789?model=pmf&top_k=5
```

### 3. Submit a Rating
```bash
curl -X POST http://localhost:8000/api/ratings \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "user_id": 456789,
    "joke_id": 5,
    "rating": 8.0
  }'
```

### 4. Get Updated Recommendations
```bash
curl http://localhost:8000/api/recommendations/456789?model=pmf&top_k=5
```

Note: Recommendations exclude already-rated jokes.

---

## Configuration

### Environment Variables
Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

**Key settings:**
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: True for development, False for production
- `CORS_ORIGINS`: Comma-separated list of allowed frontend origins
- `DEFAULT_MODEL`: Default model to use (`pmf` or `autoencoder`)
- `DEFAULT_SEED`: Random seed for reproducibility

### Models Directory
Models should be organized as:
```
models/
├── pmf/
│   ├── pmf_k10_sigmaU0.1_sigmaV0.1_bs1000.npz
│   └── pmf_k10_sigmaU0.1_sigmaV0.1_bs1000_metrics.json
└── autoencoder/
    ├── best_model.pt
    └── best_model_metrics.json
```

Copy trained models from the main recommendation pipeline to the `models/` directory.

---

## Development

### Run Tests
```bash
pytest api/tests/
```

### Database Migrations (Alembic)
Initialize Alembic:
```bash
alembic init migrations
```

Create migration:
```bash
alembic revision --autogenerate -m "Initial schema"
```

Apply migrations:
```bash
alembic upgrade head
```

### Reset Database
```bash
# Drop all tables and reinitialize
python -c "from api.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
```

---

## Docker Deployment

### Build and Run with Docker
```bash
docker build -t jokes-api:latest -f Dockerfile .
docker run -p 8000:8000 --env-file .env jokes-api:latest
```

See `Dockerfile` for containerization details.

---

## Error Handling

The API returns standardized error responses:

```json
{
  "error_code": "SESSION_NOT_FOUND",
  "message": "Session abc123 not found",
  "details": {...}
}
```

**Common HTTP Status Codes:**
- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid/inactive session
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Performance Notes

- **Model Caching**: Trained models are cached in memory after first load for fast inference
- **Recommendation Time**: ~10-100ms per user (depending on model and top-k)
- **Database**: Rating queries use indexed lookups (user_id, joke_id)
- **Concurrency**: FastAPI handles multiple concurrent requests via async/await

---

## Frontend Integration

### CORS Headers
The API enables CORS for SPAs. Ensure your frontend origin is in `CORS_ORIGINS` in `.env`:

```bash
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### Response Format
All endpoints return JSON. The frontend can parse responses directly:

```javascript
const response = await fetch('/api/recommendations/456789?model=pmf');
const data = await response.json();
console.log(data.recommendations);
```

### Session Management
- Create a session on page load: `POST /api/sessions`
- Store `session_id` in localStorage/cookies
- Pass `session_id` with rating submissions

---

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```
Ensure PostgreSQL is running: `docker-compose up -d`

### Model Not Found
```
FileNotFoundError: Model 'pmf_k10...' not found
```
Ensure trained models are in the `models/` directory. Run the recommendation training pipeline first.

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
Reinstall dependencies: `pip install -r requirements.txt`

---

## Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Pydantic Validation](https://docs.pydantic.dev/)
