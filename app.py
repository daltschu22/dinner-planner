from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

# In-memory storage for events
events = [
    {
        'id': 1,
        'title': 'Easter Dinner',
        'date': '2024-03-31 17:00',
        'location': 'Mom\'s House',
        'description': 'Annual family Easter dinner. Everyone is welcome to bring a dish!'
    },
    {
        'id': 2,
        'title': 'Summer BBQ',
        'date': '2024-07-04 16:00',
        'location': 'Backyard',
        'description': 'Independence Day celebration with grilling and fireworks.'
    },
    {
        'id': 3,
        'title': 'Thanksgiving Dinner',
        'date': '2024-11-28 16:00',
        'location': 'Grandma\'s House',
        'description': 'Traditional Thanksgiving dinner with the whole family.'
    }
]

# Helper function to get the next available ID
def get_next_id():
    if not events:
        return 1
    return max(event['id'] for event in events) + 1

@app.route('/')
def home():
    now = datetime.now()
    # Get the next 2 upcoming events (sorted by date)
    upcoming_events = sorted(
        [event for event in events], 
        key=lambda x: x['date']
    )[:2]
    return render_template('home.html', now=now, upcoming_events=upcoming_events)

@app.route('/events')
def event_list():
    now = datetime.now()
    # Sort events by date
    sorted_events = sorted(events, key=lambda x: x['date'])
    return render_template('events.html', now=now, events=sorted_events)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    now = datetime.now()
    # Find the event with the given ID
    event = next((event for event in events if event['id'] == event_id), None)
    if event is None:
        flash('Event not found', 'danger')
        return redirect(url_for('event_list'))
    return render_template('event_detail.html', now=now, event=event)

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
        new_event = {
            'id': get_next_id(),
            'title': title,
            'date': date,
            'location': location,
            'description': description
        }
        
        # Add to events list
        events.append(new_event)
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('event_detail', event_id=new_event['id']))
    
    # GET request - show the form
    return render_template('event_form.html', now=now)

@app.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def event_edit(event_id):
    now = datetime.now()
    # Find the event with the given ID
    event = next((event for event in events if event['id'] == event_id), None)
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
        event['title'] = title
        event['date'] = date
        event['location'] = location
        event['description'] = description
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # GET request - show the form with event data
    return render_template('event_form.html', now=now, event=event)

@app.route('/events/<int:event_id>/delete', methods=['GET', 'POST'])
def event_delete(event_id):
    now = datetime.now()
    # Find the event with the given ID
    event = next((event for event in events if event['id'] == event_id), None)
    if event is None:
        flash('Event not found', 'danger')
        return redirect(url_for('event_list'))
    
    if request.method == 'POST':
        # Remove the event from the list
        events[:] = [e for e in events if e['id'] != event_id]
        
        flash('Event deleted successfully!', 'success')
        return redirect(url_for('event_list'))
    
    # GET request - show confirmation page
    return render_template('event_delete.html', now=now, event=event)

if __name__ == '__main__':
    app.run(debug=True) 
