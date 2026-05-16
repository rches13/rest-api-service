# REST API Service

A scalable RESTful API for task management built with Flask, JWT authentication, and PostgreSQL. Includes an interactive Swagger UI, Docker support, and a GitHub Actions CI/CD pipeline.

## Features

- JWT-based user authentication (register & login)
- Full CRUD on tasks with per-user data isolation
- Filter tasks by status and priority
- Pagination support
- Interactive Swagger UI for testing the API in the browser
- Dockerised for local development and production deployment
- GitHub Actions CI runs the test suite on every push

## Tech Stack

- **Python / Flask** — application framework
- **Flask-JWT-Extended** — authentication
- **SQLAlchemy + PostgreSQL** — ORM and database
- **Flasgger** — Swagger UI / OpenAPI docs
- **pytest** — test suite (14 tests)
- **Docker + docker-compose** — containerisation
- **GitHub Actions** — CI/CD pipeline

## Interactive Docs (Swagger UI)

Once the server is running, open **`http://localhost:5000/docs/`** in your browser.

From there you can:
1. Use **POST /api/auth/register** to create an account
2. Copy the `token` from the response
3. Click **Authorize** (top right) and enter `Bearer <your_token>`
4. Test every endpoint directly in the browser — no curl or Postman needed

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive a JWT token |

### Tasks (requires `Authorization: Bearer <token>`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List your tasks (supports `?status=`, `?priority=`, `?page=`, `?per_page=`) |
| POST | `/api/tasks` | Create a task |
| GET | `/api/tasks/:id` | Get a single task |
| PUT | `/api/tasks/:id` | Update a task |
| DELETE | `/api/tasks/:id` | Delete a task |

**Task fields:** `title`, `description`, `status` (`todo`, `in_progress`, `done`), `priority` (`low`, `medium`, `high`)

## Getting Started

### Run with Docker (recommended)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000` and the Swagger UI at `http://localhost:5000/docs/`.

### Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials

# Start the server
python run.py
```

### Run tests

```bash
pytest tests/ -v
```

## Example Usage

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "secret"}'

# Create a task (replace <token> with the token from login)
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Build portfolio", "priority": "high"}'

# Get all tasks
curl http://localhost:5000/api/tasks \
  -H "Authorization: Bearer <token>"

# Filter by status
curl "http://localhost:5000/api/tasks?status=in_progress" \
  -H "Authorization: Bearer <token>"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost/taskapi` |
| `SECRET_KEY` | Flask secret key | `dev-secret` |
| `JWT_SECRET_KEY` | JWT signing key | `jwt-dev-secret` |
