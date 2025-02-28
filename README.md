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
- **Database**: SQLite (initially, can be upgraded later)
- **Deployment**: Vercel (planned)

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

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000`

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

## Project Phases

- **Phase 1**: Basic Flask application setup ✅
- **Phase 2**: In-memory event listing
- **Phase 3**: Event creation functionality
- **Phase 4**: Database integration
- **Phase 5**: Dish sign-up functionality
- **Phase 6**: UI polish and extra features
- **Phase 7**: Deployment

## License

MIT
