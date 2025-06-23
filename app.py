from flask import Flask, request, jsonify, g
from mongoengine import connect
from models import Ticket, ALLOWED_PRIORITIES, ALLOWED_STATUSES
from auth import auth_bp, token_required
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'tickety-secret-key'

uri= "mongodb+srv://TicketyMaster:highsec@stuproj.hyghk8a.mongodb.net/?retryWrites=true&w=majority&appName=stuproj"
connect(db='tickety_db', host=uri)

app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return "Hello, Tickety!"

@app.route('/tickets', methods=['POST'])
@token_required
def create_ticket():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400

    required_fields = ['title', 'description', 'priority']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    if data['priority'] not in ALLOWED_PRIORITIES:
        return jsonify({'error': 'Invalid priority value'}), 400

    # Assign current user as owner
    ticket = Ticket(
        user=g.current_user,
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
@token_required
def list_tickets():
    # Admin sees all tickets
    if g.current_user.role == 'admin':
        tickets = Ticket.objects()
    else:
        # Clients see only their tickets
        tickets = Ticket.objects(user=g.current_user)

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
@token_required
def get_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
    except Exception:
        return jsonify({'error': 'Ticket not found'}), 404

    # Check ownership or admin
    if ticket.user != g.current_user and g.current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    return jsonify({
        'ticket_id': ticket.ticket_id,
        'title': ticket.title,
        'description': ticket.description,
        'priority': ticket.priority,
        'status': ticket.status,
        'created_at': ticket.created_at.isoformat()
    }), 200

@app.route('/tickets/<int:ticket_id>', methods=['PATCH'])
@token_required
def update_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
    except Exception:
        return jsonify({'error': 'Ticket not found'}), 404

    # Check ownership or admin
    if ticket.user != g.current_user and g.current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400

    if 'title' in data:
        ticket.title = data['title']

    if 'description' in data:
        ticket.description = data['description']

    if 'priority' in data:
        if data['priority'] not in ALLOWED_PRIORITIES:
            return jsonify({'error': 'Invalid priority'}), 400
        ticket.priority = data['priority']

    if 'status' in data:
        if data['status'] not in ALLOWED_STATUSES:
            return jsonify({'error': 'Invalid status'}), 400
        ticket.status = data['status']

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
@token_required
def delete_ticket(ticket_id):
    if g.current_user.role != 'admin':
        return jsonify({'error': 'Admin privilege required'}), 403

    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        ticket.delete()
        return jsonify({'message': 'Ticket deleted'}), 200
    except Exception:
        return jsonify({'error': 'Ticket not found'}), 404
@app.route('/me', methods=['GET'])
@token_required
def get_current_user():
    user = g.current_user
    return jsonify({
        'username': user.username,
        'role': user.role
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, port=port, host='0.0.0.0')
