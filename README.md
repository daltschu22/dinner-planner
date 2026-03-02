# Family Dinner Planner

A web application to coordinate family dinner events, track locations, and manage what dishes each person is bringing.

## Technology Stack

- Backend: Python + FastAPI
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Database: SQLite (local + Railway via mounted volume)
- Deployment: Railway

## Local Development

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` (or copy from `.env.example`) and set:

```env
SECRET_KEY=change-me
APP_ENV=development
DATABASE_PATH=dinner_planner.db
```

5. Run locally:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. Open `http://127.0.0.1:8000`.

## Railway Deployment (Persistent SQLite)

This repository includes:

- `railway.toml`
- `Procfile`

### Deploy steps

1. Create a Railway project from this GitHub repository.
2. Add a Railway Volume to the service.
3. Mount the volume at `/data`.
4. Set environment variables:

```env
SECRET_KEY=your-secret-key
APP_ENV=production
DATABASE_PATH=/data/dinner_planner.db
```

5. Deploy.

Startup command used by Railway:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Optional Redis backend (not required):

```env
DB_BACKEND=redis
REDIS_URL=redis://...
```

## Notes

- SQLite persistence depends on setting `DATABASE_PATH` to your mounted volume path.
- Redis support remains optional and disabled by default.

## License

MIT
