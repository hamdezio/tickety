from flask import Flask, request, jsonify
from mongoengine import connect, Document, StringField, DateTimeField, SequenceField
from mongoengine.errors import DoesNotExist
import datetime

# Connect to local MongoDB (adjust host/port if needed)
connect('tickety_db', host='localhost', port=27017)

app = Flask(__name__)

# Allowed values for priority and status fields
ALLOWED_PRIORITIES = {'low', 'medium', 'high'}
ALLOWED_STATUSES = {'open', 'in progress', 'resolved', 'closed'}

# MongoEngine Document (Model) for Ticket with auto-incrementing ticket_id
class Ticket(Document):
    ticket_id = SequenceField(primary_key=True)  # Auto-increment integer ID
    title = StringField(required=True)
    description = StringField(required=True)
    priority = StringField(required=True, choices=ALLOWED_PRIORITIES)
    status = StringField(default='open', choices=ALLOWED_STATUSES)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

# Catch-all for unmatched routes
@app.route('/<path:any_path>')
def catch_all(any_path):
    print(f"Unmatched route accessed: /{any_path}")
    return jsonify({"error": "Route not found"}), 404

@app.route('/')
def home():
    return "Hello, Tickety!"

@app.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json()

    if data is None:
        return jsonify({'error': 'Missing or invalid JSON data'}), 400

    required_fields = ['title', 'description', 'priority']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    if data['priority'] not in ALLOWED_PRIORITIES:
        return jsonify({'error': 'Invalid priority. Must be one of: low, medium, high'}), 400

    ticket = Ticket(
        title=data['title'],
        description=data['description'],
        priority=data['priority'],
        status='open'
    )
    ticket.save()

    return jsonify({
        'ticket_id': ticket.ticket_id,
        'title': ticket.title,
        'description': ticket.description,
        'priority': ticket.priority,
        'status': ticket.status,
        'created_at': ticket.created_at.isoformat()
    }), 201

@app.route('/tickets', methods=['GET'])
def list_tickets():
    tickets = Ticket.objects()
    result = []
    for t in tickets:
        result.append({
            'ticket_id': t.ticket_id,
            'title': t.title,
            'description': t.description,
            'priority': t.priority,
            'status': t.status,
            'created_at': t.created_at.isoformat()
        })
    return jsonify(result), 200

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        return jsonify({
            'ticket_id': ticket.ticket_id,
            'title': ticket.title,
            'description': ticket.description,
            'priority': ticket.priority,
            'status': ticket.status,
            'created_at': ticket.created_at.isoformat()
        }), 200
    except DoesNotExist:
        return jsonify({'error': 'Ticket not found'}), 404
    except Exception:
        return jsonify({'error': 'Invalid ticket ID'}), 400

@app.route('/tickets/<int:ticket_id>', methods=['PATCH'])
def update_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
    except DoesNotExist:
        return jsonify({'error': 'Ticket not found'}), 404
    except Exception:
        return jsonify({'error': 'Invalid ticket ID'}), 400

    update_data = request.get_json()
    if update_data is None:
        return jsonify({'error': 'Missing or invalid JSON data'}), 400

    if 'title' in update_data:
        ticket.title = update_data['title']

    if 'description' in update_data:
        ticket.description = update_data['description']

    if 'priority' in update_data:
        if update_data['priority'] not in ALLOWED_PRIORITIES:
            return jsonify({'error': 'Invalid priority'}), 400
        ticket.priority = update_data['priority']

    if 'status' in update_data:
        if update_data['status'] not in ALLOWED_STATUSES:
            return jsonify({'error': 'Invalid status'}), 400
        ticket.status = update_data['status']

    ticket.save()

    return jsonify({
        'ticket_id': ticket.ticket_id,
        'title': ticket.title,
        'description': ticket.description,
        'priority': ticket.priority,
        'status': ticket.status,
        'created_at': ticket.created_at.isoformat()
    }), 200

@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        ticket.delete()
        return jsonify({'message': 'Ticket deleted successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'Ticket not found'}), 404
    except Exception:
        return jsonify({'error': 'Invalid ticket ID'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5002)
