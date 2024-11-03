from flask import render_template, request, send_file, redirect, url_for, flash, jsonify, Blueprint, session
from datetime import datetime, timedelta
import os
import uuid
import secrets
from src.database import notes_collection
from bson.objectid import ObjectId
from io import BytesIO

notes = Blueprint('notes_app', __name__)

UPLOAD_FOLDER = 'downloads'

# Ensure the downloads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@notes.route('/all_notes', methods=['GET'])
def all_notes():
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    # Fetch only the notes for the specific user
    notes_list = list(notes_collection.find({"user_id": ObjectId(user_id)}))
    return render_template('all_notes.html', notes=notes_list)

@notes.route('/note', methods=['GET', 'POST'])
def create_note():
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        note_title = request.form.get('title', '')
        note_content = request.form.get('note', '')
        formatted_content = request.form.get('formatted_content', '')
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add title and date to the formatted content
        header = f"<h2>{note_title}</h2><p>Date: {date}</p>"
        formatted_content = header + formatted_content
        
        note_id = str(uuid.uuid4())
        
        # Save the note for the specific user
        notes_collection.insert_one({
            "user_id": ObjectId(user_id),
            "note_id": note_id,
            "title": note_title,
            "content": note_content,
            "formatted_content": formatted_content,
            "created_at": datetime.now(),
            "expires_at": None
        })
        
        flash('Your note has been saved successfully!', 'info')
        return redirect(url_for('notes_app.all_notes'))

    return render_template('create.html')

@notes.route('/view/<note_id>', methods=['GET'])
def view_note(note_id):
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    # Fetch the note for the specific user
    note = notes_collection.find_one({"note_id": note_id, "user_id": ObjectId(user_id)})
    if note:
        return render_template(
            'view_note.html', 
            note_title=note["title"],
            note_content=note["content"].strip(),
            note_id=note_id,
            formatted_content=note["formatted_content"]
        )
    return "Note not found", 404



@notes.route('/download/<note_id>')
def download_note(note_id):
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    note = notes_collection.find_one({"note_id": note_id, "user_id": ObjectId(user_id)})
    if note:
        # Generate the content in memory instead of saving it to disk
        file_content = f"Title: {note['title']}\n"
        file_content += f"Date: {note['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        file_content += note["content"]
        
        # Use BytesIO to create a file-like object in memory
        file_stream = BytesIO(file_content.encode('utf-8'))
        
        # Set a filename for the download
        download_filename = f"{note['title']}.txt"
        
        return send_file(file_stream, as_attachment=True, download_name=download_filename)
    
    return "Note not found", 404


@notes.route('/edit/<note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    note = notes_collection.find_one({"note_id": note_id, "user_id": ObjectId(user_id)})
    if request.method == 'POST' and note:
        note_title = request.form.get('title', '')
        note_content = request.form.get('note', '')
        formatted_content = request.form.get('formatted_content', '')
        
        notes_collection.update_one(
            {"note_id": note_id, "user_id": ObjectId(user_id)},
            {"$set": {
                "title": note_title,
                "content": note_content,
                "formatted_content": formatted_content,
                "updated_at": datetime.now()
            }}
        )
        
        flash('Your note has been updated successfully!', 'info')
        return redirect(url_for('notes_app.all_notes'))

    return render_template('edit_note.html', note=note)

@notes.route('/delete/<note_id>', methods=['POST'])
def delete_note(note_id):
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    notes_collection.delete_one({"note_id": note_id, "user_id": ObjectId(user_id)})
    flash('Note deleted successfully!', 'info')
    return redirect(url_for('notes_app.all_notes'))

@notes.route('/share/<note_id>', methods=['GET'])
def share_note_link(note_id):
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    note = notes_collection.find_one({"note_id": note_id, "user_id": ObjectId(user_id)})
    if note:
        share_token = secrets.token_urlsafe(16)
        expiration_time = datetime.now() + timedelta(hours=24)
        
        notes_collection.update_one(
            {"note_id": note_id},
            {"$set": {"share_token": share_token, "expires_at": expiration_time}}
        )
        
        share_link = url_for('notes_app.view_shared_note', note_id=note_id, token=share_token, _external=True)
        return jsonify({"share_link": share_link}), 200
    return jsonify({"error": "Note not found"}), 404

@notes.route('/shared/<note_id>/<token>')
def view_shared_note(note_id, token):
    note = notes_collection.find_one({"note_id": note_id, "share_token": token})
    if note:
        if note.get("expires_at") and datetime.now() > note["expires_at"]:
            notes_collection.update_one({"note_id": note_id}, {"$unset": {"share_token": "", "expires_at": ""}})
            return "The link has expired.", 410
        return render_template(
            'share_view.html', 
            note_title=note["title"],
            note_content=note["content"].strip(),
            note_id=note_id,
            formatted_content=note["formatted_content"]
        )
    return "Invalid or expired link.", 404
