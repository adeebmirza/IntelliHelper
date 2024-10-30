from flask import Blueprint, render_template, request, redirect, url_for, session
from bson.objectid import ObjectId
#from src.database import todos_collection

todo = Blueprint('todo_app', __name__)

# Home route - Displays all tasks
@todo.route('/todo_app', methods=['GET', 'POST'])
def index():
    from src.database import todos_collection
    user_id = session.get('user', {}).get('_id')  # Safer way to access session data
    if not user_id:
        return redirect(url_for('auth.login'))
    
    tasks = todos_collection.find({'user_id': ObjectId(user_id)})  # Only get the logged-in user's tasks
    return render_template('todo_home.html', tasks=tasks)

# Add task route
@todo.route('/add_task', methods=['GET', 'POST'])
def add_task():
    from src.database import todos_collection
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        task = request.form['task']
        todos_collection.insert_one({'task': task, 'status': 'pending', 'user_id': ObjectId(user_id)})
        return redirect(url_for('todo_app.index'))  # Fix route reference
    return render_template('add_task.html')

# Edit task route
@todo.route('/edit_task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    from src.database import todos_collection
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    task = todos_collection.find_one({"_id": ObjectId(task_id), "user_id": ObjectId(user_id)})
    if request.method == 'POST':
        updated_task = request.form['task']
        todos_collection.update_one({'_id': ObjectId(task_id)}, {'$set': {'task': updated_task}})
        return redirect(url_for('todo_app.index'))  # Fix route reference
    return render_template('edit_task.html', task=task)

# Delete task route
@todo.route('/delete_task/<task_id>')
def delete_task(task_id):
    from src.database import todos_collection
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    todos_collection.delete_one({'_id': ObjectId(task_id), 'user_id': ObjectId(user_id)})
    return redirect(url_for('todo_app.index'))  # Fix route reference

# Mark task as completed
@todo.route('/complete_task/<task_id>')
def complete_task(task_id):
    from src.database import todos_collection
    user_id = session.get('user', {}).get('_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    todos_collection.update_one({'_id': ObjectId(task_id), 'user_id': ObjectId(user_id)}, {'$set': {'status': 'completed'}})
    return redirect(url_for('todo_app.index'))  # Fix route reference
