import os
import secrets
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from database import get_db

load_dotenv()


def get_session_secret_key() -> str:
    configured = os.environ.get("SECRET_KEY")
    if configured:
        return configured

    candidate_paths = []
    secret_file = os.environ.get("SECRET_KEY_FILE")
    if secret_file:
        candidate_paths.append(secret_file)
    if os.path.isdir("/data"):
        candidate_paths.append("/data/.dinner_secret_key")
    candidate_paths.append(".dinner_secret_key")

    for path in candidate_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                existing = handle.read().strip()
                if existing:
                    return existing

    generated = secrets.token_urlsafe(48)
    for path in candidate_paths:
        try:
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(generated)
            os.chmod(path, 0o600)
            return generated
        except OSError:
            continue

    return generated


app = FastAPI(title="Family Dinner Planner")
app.add_middleware(SessionMiddleware, secret_key=get_session_secret_key())
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
db = get_db()


def add_flash(request: Request, category: str, message: str) -> None:
    flashes = request.session.get("flashes", [])
    flashes.append({"category": category, "message": message})
    request.session["flashes"] = flashes


def pop_flashes(request: Request):
    flashes = request.session.get("flashes", [])
    request.session["flashes"] = []
    return flashes


def render(request: Request, template_name: str, **context):
    context.update(
        {
            "request": request,
            "now": datetime.now(),
            "flashes": pop_flashes(request),
        }
    )
    return templates.TemplateResponse(template_name, context)


@app.get("/")
def home(request: Request):
    upcoming_events = db.get_upcoming_events(limit=2)

    for event in upcoming_events:
        event_id = event["id"]
        dishes = db.get_dishes_for_event(event_id)
        event["dishes"] = dishes

        category_counts = {}
        for dish in dishes:
            category_name = dish["category_name"]
            category_counts[category_name] = category_counts.get(category_name, 0) + 1

        event["category_counts"] = category_counts

    return render(request, "home.html", upcoming_events=upcoming_events)


@app.get("/events")
def event_list(request: Request):
    now = datetime.now()
    all_events = db.get_events()

    upcoming_events = []
    past_events = []

    for event in all_events:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d %H:%M")
        if event_date >= now:
            upcoming_events.append(event)
        else:
            past_events.append(event)

    upcoming_events = sorted(upcoming_events, key=lambda x: x["date"])
    past_events = sorted(past_events, key=lambda x: x["date"], reverse=True)
    sorted_events = upcoming_events + past_events

    return render(
        request,
        "events.html",
        events=sorted_events,
        upcoming_count=len(upcoming_events),
        past_count=len(past_events),
    )


@app.get("/events/{event_id}")
def event_detail(request: Request, event_id: int):
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    event_date = datetime.strptime(event["date"], "%Y-%m-%d %H:%M")
    dishes = db.get_dishes_for_event(event_id)
    categories = db.get_dish_categories()

    category_counts = {}
    for dish in dishes:
        category_id = dish["category_id"]
        category_counts[category_id] = category_counts.get(category_id, 0) + 1

    return render(
        request,
        "event_detail.html",
        event=event,
        event_date=event_date,
        dishes=dishes,
        categories=categories,
        category_counts=category_counts,
    )


@app.get("/events/add")
def event_add_form(request: Request):
    return render(request, "event_form.html")


@app.post("/events/add")
def event_add(
    request: Request,
    title: str | None = Form(default=None),
    date: str | None = Form(default=None),
    location: str | None = Form(default=None),
    description: str = Form(default=""),
):
    if not title or not date or not location:
        add_flash(request, "danger", "Please fill in all required fields")
        return render(request, "event_form.html")

    date = date.replace("T", " ")
    event = db.add_event(title, date, location, description)

    add_flash(request, "success", "Event created successfully!")
    return RedirectResponse(url=request.url_for("event_detail", event_id=str(event["id"])), status_code=303)


@app.get("/events/{event_id}/edit")
def event_edit_form(request: Request, event_id: int):
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    return render(request, "event_form.html", event=event)


@app.post("/events/{event_id}/edit")
def event_edit(
    request: Request,
    event_id: int,
    title: str | None = Form(default=None),
    date: str | None = Form(default=None),
    location: str | None = Form(default=None),
    description: str = Form(default=""),
):
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    if not title or not date or not location:
        add_flash(request, "danger", "Please fill in all required fields")
        return render(request, "event_form.html", event=event)

    date = date.replace("T", " ")
    updated_event = db.update_event(event_id, title, date, location, description)
    if updated_event:
        add_flash(request, "success", "Event updated successfully!")
        return RedirectResponse(url=request.url_for("event_detail", event_id=str(event_id)), status_code=303)

    add_flash(request, "danger", "Failed to update event")
    return RedirectResponse(url=request.url_for("event_list"), status_code=303)


@app.get("/events/{event_id}/delete")
def event_delete_form(request: Request, event_id: int):
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    return render(request, "event_delete.html", event=event)


@app.post("/events/{event_id}/delete")
def event_delete(request: Request, event_id: int):
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    success = db.delete_event(event_id)
    if success:
        add_flash(request, "success", "Event deleted successfully!")
    else:
        add_flash(request, "danger", "Failed to delete event")

    return RedirectResponse(url=request.url_for("event_list"), status_code=303)


@app.get("/events/{event_id}/dishes/add")
def dish_add_form(request: Request, event_id: int):
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    categories = db.get_dish_categories()
    return render(request, "dish_form.html", event=event, categories=categories)


@app.post("/events/{event_id}/dishes/add")
def dish_add(
    request: Request,
    event_id: int,
    name: str | None = Form(default=None),
    category_id: str | None = Form(default=None),
    person_name: str | None = Form(default=None),
    description: str = Form(default=""),
    serves: str = Form(default="0"),
):
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    categories = db.get_dish_categories()

    if not name or not category_id or not person_name:
        add_flash(request, "danger", "Please fill in all required fields")
        return render(request, "dish_form.html", event=event, categories=categories)

    try:
        category_id_int = int(category_id)
        serves_int = int(serves)
    except ValueError:
        add_flash(request, "danger", "Invalid data provided")
        return render(request, "dish_form.html", event=event, categories=categories)

    try:
        db.add_dish(event_id, name, category_id_int, person_name, description, serves_int)
        add_flash(request, "success", "Dish added successfully!")
        return RedirectResponse(url=request.url_for("event_detail", event_id=str(event_id)), status_code=303)
    except ValueError as exc:
        add_flash(request, "danger", str(exc))
        return render(request, "dish_form.html", event=event, categories=categories)


@app.get("/dishes/{dish_id}/edit")
def dish_edit_form(request: Request, dish_id: int):
    dish = db.get_dish_by_id(dish_id)
    if dish is None:
        add_flash(request, "danger", "Dish not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    event_id = dish["event_id"]
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    categories = db.get_dish_categories()
    return render(request, "dish_form.html", event=event, dish=dish, categories=categories)


@app.post("/dishes/{dish_id}/edit")
def dish_edit(
    request: Request,
    dish_id: int,
    name: str | None = Form(default=None),
    category_id: str | None = Form(default=None),
    person_name: str | None = Form(default=None),
    description: str = Form(default=""),
    serves: str = Form(default="0"),
):
    dish = db.get_dish_by_id(dish_id)
    if dish is None:
        add_flash(request, "danger", "Dish not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    event_id = dish["event_id"]
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    categories = db.get_dish_categories()

    if not name or not category_id or not person_name:
        add_flash(request, "danger", "Please fill in all required fields")
        return render(request, "dish_form.html", event=event, dish=dish, categories=categories)

    try:
        category_id_int = int(category_id)
        serves_int = int(serves)
    except ValueError:
        add_flash(request, "danger", "Invalid data provided")
        return render(request, "dish_form.html", event=event, dish=dish, categories=categories)

    try:
        updated_dish = db.update_dish(dish_id, name, category_id_int, person_name, description, serves_int)
        if updated_dish:
            add_flash(request, "success", "Dish updated successfully!")
            return RedirectResponse(url=request.url_for("event_detail", event_id=str(event_id)), status_code=303)

        add_flash(request, "danger", "Failed to update dish")
        return RedirectResponse(url=request.url_for("event_detail", event_id=str(event_id)), status_code=303)
    except ValueError as exc:
        add_flash(request, "danger", str(exc))
        return render(request, "dish_form.html", event=event, dish=dish, categories=categories)


@app.get("/dishes/{dish_id}/delete")
def dish_delete_form(request: Request, dish_id: int):
    dish = db.get_dish_by_id(dish_id)
    if dish is None:
        add_flash(request, "danger", "Dish not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    event_id = dish["event_id"]
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    return render(request, "dish_delete.html", event=event, dish=dish)


@app.post("/dishes/{dish_id}/delete")
def dish_delete(request: Request, dish_id: int):
    dish = db.get_dish_by_id(dish_id)
    if dish is None:
        add_flash(request, "danger", "Dish not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    event_id = dish["event_id"]
    event = db.get_event_by_id(event_id)
    if event is None:
        add_flash(request, "danger", "Event not found")
        return RedirectResponse(url=request.url_for("event_list"), status_code=303)

    success = db.delete_dish(dish_id)
    if success:
        add_flash(request, "success", "Dish deleted successfully!")
    else:
        add_flash(request, "danger", "Failed to delete dish")

    return RedirectResponse(url=request.url_for("event_detail", event_id=str(event_id)), status_code=303)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
