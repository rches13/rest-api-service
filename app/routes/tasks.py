from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.task import Task

tasks_bp = Blueprint('tasks', __name__)

VALID_STATUSES = {'todo', 'in_progress', 'done'}
VALID_PRIORITIES = {'low', 'medium', 'high'}


@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    List all tasks for the authenticated user.
    ---
    tags:
      - Tasks
    security:
      - BearerAuth: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [todo, in_progress, done]
      - in: query
        name: priority
        type: string
        enum: [low, medium, high]
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 10
    responses:
      200:
        description: Paginated list of tasks
      401:
        description: Missing or invalid token
    """
    user_id = int(get_jwt_identity())
    query = Task.query.filter_by(user_id=user_id)

    status = request.args.get('status')
    priority = request.args.get('priority')
    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)
    if priority and priority in VALID_PRIORITIES:
        query = query.filter_by(priority=priority)

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    paginated = query.order_by(Task.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'tasks': [t.to_dict() for t in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'page': page,
    })


@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """
    Create a new task.
    ---
    tags:
      - Tasks
    security:
      - BearerAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [title]
          properties:
            title:
              type: string
              example: Build portfolio site
            description:
              type: string
              example: Set up Next.js and deploy to Vercel
            status:
              type: string
              enum: [todo, in_progress, done]
              default: todo
            priority:
              type: string
              enum: [low, medium, high]
              default: medium
    responses:
      201:
        description: Task created
      400:
        description: Missing or invalid fields
      401:
        description: Missing or invalid token
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': 'title is required'}), 400

    status = data.get('status', 'todo')
    priority = data.get('priority', 'medium')
    if status not in VALID_STATUSES:
        return jsonify({'error': f'status must be one of {sorted(VALID_STATUSES)}'}), 400
    if priority not in VALID_PRIORITIES:
        return jsonify({'error': f'priority must be one of {sorted(VALID_PRIORITIES)}'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description'),
        status=status,
        priority=priority,
        user_id=user_id,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """
    Get a single task by ID.
    ---
    tags:
      - Tasks
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Task details
      401:
        description: Missing or invalid token
      404:
        description: Task not found
    """
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    return jsonify(task.to_dict())


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """
    Update a task.
    ---
    tags:
      - Tasks
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            status:
              type: string
              enum: [todo, in_progress, done]
            priority:
              type: string
              enum: [low, medium, high]
    responses:
      200:
        description: Updated task
      400:
        description: Invalid field values
      401:
        description: Missing or invalid token
      404:
        description: Task not found
    """
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}

    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return jsonify({'error': f'status must be one of {sorted(VALID_STATUSES)}'}), 400
        task.status = data['status']
    if 'priority' in data:
        if data['priority'] not in VALID_PRIORITIES:
            return jsonify({'error': f'priority must be one of {sorted(VALID_PRIORITIES)}'}), 400
        task.priority = data['priority']

    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """
    Delete a task.
    ---
    tags:
      - Tasks
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      204:
        description: Task deleted
      401:
        description: Missing or invalid token
      404:
        description: Task not found
    """
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return '', 204
