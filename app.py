from flask import Flask, request, jsonify

app = Flask(__name__)


tickets = []
@app.route('/<path:any_path>')
def catch_all(any_path):
    print(f"Unmatched route accessed: /{any_path}")
    return jsonify({"error": "Route not found"}), 404

@app.route('/')
def home():
    return "Hello, Tickety!"
@app.route('/tickets', methods=['POST'])
def create_ticket():
    print("POST /tickets route hit")
    required_fields = ['title', 'description', 'priority']
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid or missing JSON data'}), 400

    if not all(field in data for field in required_fields):
        return jsonify({'error':'Missing required fields'}), 400
    ticket = {
        "id": len(tickets) + 1,
        "title": data['title'],
        "description": data['description'],
        "priority": data['priority'],
        "status": "open"}
    tickets.append(ticket)
    return jsonify(ticket), 201





if __name__ == '__main__':
    app.run(debug=True, port=5001)
