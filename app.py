from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import datetime
import os
from dotenv import load_dotenv
from database import get_db

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')  # Get secret key from environment variable

# Get the database instance
db = get_db()

@app.route('/')
def home():
    now = datetime.now()
    # Get upcoming events (sorted by date, only future events)
    upcoming_events = db.get_upcoming_events(limit=2)
    
    # Get dish information for each event
    for event in upcoming_events:
        event_id = event['id']
        dishes = db.get_dishes_for_event(event_id)
        event['dishes'] = dishes
        
        # Count dishes by category
        category_counts = {}
        for dish in dishes:
            category_name = dish['category_name']
            if category_name in category_counts:
                category_counts[category_name] += 1
            else:
                category_counts[category_name] = 1
        
        event['category_counts'] = category_counts
    
    return render_template('home.html', now=now, upcoming_events=upcoming_events)

@app.route('/events')
def event_list():
    now = datetime.now()
    
    # Get all events
    all_events = db.get_events()
    
    # Separate events into upcoming and past
    upcoming_events = []
    past_events = []
    
    for event in all_events:
        event_date = datetime.strptime(event['date'], '%Y-%m-%d %H:%M')
        if event_date >= now:
            upcoming_events.append(event)
        else:
            past_events.append(event)
    
    # Sort both lists by date
    upcoming_events = sorted(upcoming_events, key=lambda x: x['date'])
    past_events = sorted(past_events, key=lambda x: x['date'], reverse=True)
    
    # Combine the lists with upcoming events first
    sorted_events = upcoming_events + past_events
    
    return render_template('events.html', now=now, events=sorted_events, 
                          upcoming_count=len(upcoming_events), past_count=len(past_events))

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    now = datetime.now()
    # Find the event with the given ID
    event = db.get_event_by_id(event_id)
    if event is None:
        flash('Event not found', 'danger')
        return redirect(url_for('event_list'))
    
    # Convert the event date string to a datetime object for comparison in the template
    event_date = datetime.strptime(event['date'], '%Y-%m-%d %H:%M')
    
    # Get dishes for this event
    dishes = db.get_dishes_for_event(event_id)
    
    # Get all dish categories
    categories = db.get_dish_categories()
    
    # Count dishes by category
    category_counts = {}
    for dish in dishes:
        category_id = dish['category_id']
        if category_id in category_counts:
            category_counts[category_id] += 1
        else:
            category_counts[category_id] = 1
    
    return render_template('event_detail.html', now=now, event=event, event_date=event_date,
                          dishes=dishes, categories=categories, category_counts=category_counts)

@app.route('/events/add', methods=['GET', 'POST'])
def event_add():
    now = datetime.now()
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        date = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')
        
        # Validate form data
        if not title or not date or not location:
            flash('Please fill in all required fields', 'danger')
            return render_template('event_form.html', now=now)
        
        # Format the date (convert from datetime-local format to our format)
        date = date.replace('T', ' ')
        
        # Create new event
        event = db.add_event(title, date, location, description)
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('event_detail', event_id=event['id']))
    
    # GET request - show the form
    return render_template('event_form.html', now=now)

@app.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def event_edit(event_id):
    now = datetime.now()
    # Find the event with the given ID
    event = db.get_event_by_id(event_id)
    if event is None:
        flash('Event not found', 'danger')
        return redirect(url_for('event_list'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        date = request.form.get('date')
        location = request.form.get('location')
        description = request.form.get('description')
        
        # Validate form data
        if not title or not date or not location:
            flash('Please fill in all required fields', 'danger')
            return render_template('event_form.html', now=now, event=event)
        
        # Format the date (convert from datetime-local format to our format)
        date = date.replace('T', ' ')
        
        # Update event
        updated_event = db.update_event(event_id, title, date, location, description)
        if updated_event:
            flash('Event updated successfully!', 'success')
            return redirect(url_for('event_detail', event_id=event_id))
        else:
            flash('Failed to update event', 'danger')
            return redirect(url_for('event_list'))
    
    # GET request - show the form with event data
    return render_template('event_form.html', now=now, event=event)

@app.route('/events/<int:event_id>/delete', methods=['GET', 'POST'])
def event_delete(event_id):
    now = datetime.now()
    # Find the event with the given ID
    event = db.get_event_by_id(event_id)
    if event is None:
        flash('Event not found', 'danger')
        return redirect(url_for('event_list'))
    
    if request.method == 'POST':
        # Delete the event
        success = db.delete_event(event_id)
        
        if success:
            flash('Event deleted successfully!', 'success')
        else:
            flash('Failed to delete event', 'danger')
        
        return redirect(url_for('event_list'))
    
    # GET request - show confirmation page
    return render_template('event_delete.html', now=now, event=event)

# Dish routes - Phase 5

@app.route('/events/<int:event_id>/dishes/add', methods=['GET', 'POST'])
def dish_add(event_id):
    now = datetime.now()
    # Find the event with the given ID
    event = db.get_event_by_id(event_id)
    if event is None:
        flash('Event not found', 'danger')
        return redirect(url_for('event_list'))
    
    # Get all dish categories
    categories = db.get_dish_categories()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        person_name = request.form.get('person_name')
        description = request.form.get('description', '')
        serves = request.form.get('serves', '0')
        
        # Validate form data
        if not name or not category_id or not person_name:
            flash('Please fill in all required fields', 'danger')
            return render_template('dish_form.html', now=now, event=event, categories=categories)
        
        # Convert category_id and serves to integers
        try:
            category_id = int(category_id)
            serves = int(serves)
        except ValueError:
            flash('Invalid data provided', 'danger')
            return render_template('dish_form.html', now=now, event=event, categories=categories)
        
        # Create new dish
        try:
            dish = db.add_dish(event_id, name, category_id, person_name, description, serves)
            flash('Dish added successfully!', 'success')
            return redirect(url_for('event_detail', event_id=event_id))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('dish_form.html', now=now, event=event, categories=categories)
    
    # GET request - show the form
    return render_template('dish_form.html', now=now, event=event, categories=categories)

@app.route('/dishes/<int:dish_id>/edit', methods=['GET', 'POST'])
def dish_edit(dish_id):
    now = datetime.now()
    # Find the dish with the given ID
    dish = db.get_dish_by_id(dish_id)
    if dish is None:
        flash('Dish not found', 'danger')
        return redirect(url_for('event_list'))
    
    # Find the event for this dish
    event_id = dish['event_id']
    event = db.get_event_by_id(event_id)
    if event is None:
        flash('Event not found', 'danger')
        return redirect(url_for('event_list'))
    
    # Get all dish categories
    categories = db.get_dish_categories()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        person_name = request.form.get('person_name')
        description = request.form.get('description', '')
        serves = request.form.get('serves', '0')
        
        # Validate form data
        if not name or not category_id or not person_name:
            flash('Please fill in all required fields', 'danger')
            return render_template('dish_form.html', now=now, event=event, dish=dish, categories=categories)
        
        # Convert category_id and serves to integers
        try:
            category_id = int(category_id)
            serves = int(serves)
        except ValueError:
            flash('Invalid data provided', 'danger')
            return render_template('dish_form.html', now=now, event=event, dish=dish, categories=categories)
        
        # Update dish
        try:
            updated_dish = db.update_dish(dish_id, name, category_id, person_name, description, serves)
            if updated_dish:
                flash('Dish updated successfully!', 'success')
                return redirect(url_for('event_detail', event_id=event_id))
            else:
                flash('Failed to update dish', 'danger')
                return redirect(url_for('event_detail', event_id=event_id))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('dish_form.html', now=now, event=event, dish=dish, categories=categories)
    
    # GET request - show the form with dish data
    return render_template('dish_form.html', now=now, event=event, dish=dish, categories=categories)

@app.route('/dishes/<int:dish_id>/delete', methods=['GET', 'POST'])
def dish_delete(dish_id):
    now = datetime.now()
    # Find the dish with the given ID
    dish = db.get_dish_by_id(dish_id)
    if dish is None:
        flash('Dish not found', 'danger')
        return redirect(url_for('event_list'))
    
    # Find the event for this dish
    event_id = dish['event_id']
    event = db.get_event_by_id(event_id)
    if event is None:
        flash('Event not found', 'danger')
        return redirect(url_for('event_list'))
    
    if request.method == 'POST':
        # Delete the dish
        success = db.delete_dish(dish_id)
        
        if success:
            flash('Dish deleted successfully!', 'success')
        else:
            flash('Failed to delete dish', 'danger')
        
        return redirect(url_for('event_detail', event_id=event_id))
    
    # GET request - show confirmation page
    return render_template('dish_delete.html', now=now, event=event, dish=dish)

if __name__ == '__main__':
    app.run(debug=True) 
