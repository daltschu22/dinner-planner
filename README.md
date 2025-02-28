# Family Dinner Planner

A web application to help coordinate family dinner events, track locations, and manage what dishes each person is bringing.

## Features (Planned)

- Create and manage dinner events with date, time, and location
- Sign up to bring specific dishes to events
- Categorize dishes (appetizers, mains, sides, desserts, drinks)
- View upcoming events and what dishes are planned

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: 
  - SQLite (local development)
  - Redis (production on Vercel)
- **Deployment**: Vercel

## Local Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/dinner-planner.git
   cd dinner-planner
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```
   
   Edit the `.env` file to set your secret key and other configuration options.

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to `http://127.0.0.1:5000`

### Container Setup (Using Podman)

If you prefer to use containers, you can use Podman to run the application:

1. Make sure Podman is installed on your system.

2. Use the provided script to manage the container:
   ```
   # Start the application
   ./podman.sh start
   
   # View container logs
   ./podman.sh logs
   
   # Check container status
   ./podman.sh status
   
   # Stop the application
   ./podman.sh stop
   
   # Restart the application
   ./podman.sh restart
   
   # Clean up CNI configurations (if you see CNI warnings)
   ./podman.sh cleanup
   
   # Show help
   ./podman.sh help
   ```

3. Open your browser and navigate to `http://localhost:5000`

## Deployment to Vercel

This application is configured for deployment on Vercel. To deploy:

1. Sign up for a [Vercel account](https://vercel.com/signup) if you don't have one.

2. Set up a Redis database:
   - You can use [Redis Cloud](https://redis.com/try-free/) which offers a free tier
   - Or any other Redis provider that gives you a connection URL

3. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

4. Login to Vercel:
   ```
   vercel login
   ```

5. Set up environment variables in Vercel:
   ```
   vercel env add REDIS_URL
   ```
   When prompted, enter your Redis connection URL (e.g., `redis://username:password@host:port`).
   
   Also add a secure SECRET_KEY:
   ```
   vercel env add SECRET_KEY
   ```

6. Deploy the application:
   ```
   vercel
   ```

7. For production deployment:
   ```
   vercel --prod
   ```

The application uses the following configuration files for Vercel deployment:
- `vercel.json` - Configuration for the Vercel platform
- `api/index.py` - Entry point for the Flask application
- `.vercelignore` - Specifies files to exclude from deployment

## Project Phases

- **Phase 1**: Basic Flask application setup ✅
- **Phase 2**: In-memory event listing ✅
- **Phase 3**: Event creation functionality ✅
- **Phase 4**: Database integration ✅
- **Phase 5**: Dish sign-up functionality ✅
- **Phase 6**: UI polish and extra features
- **Phase 7**: Deployment

## License

MIT
