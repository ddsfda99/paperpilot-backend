from flask import Blueprint, request, jsonify
from models import db, Note

note_bp = Blueprint('note', __name__)

@note_bp.route('/api/notes', methods=['GET'])
def get_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notes])

@note_bp.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    note = Note(
        title=data.get('title', ''),
        content=data.get('content', '')
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201

@note_bp.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    db.session.commit()
    return jsonify(note.to_dict())

@note_bp.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True})
