from functools import wraps
from flask import request, jsonify
from db.mongo import mongo_db
from bson.objectid import ObjectId

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user email from headers (sent by frontend)
            user_email = request.headers.get('X-User-Email')
            
            if not user_email:
                return jsonify({'message': 'User email header is missing'}), 401

            # Find user in database
            user = mongo_db.users.find_one({"email": user_email})
            if not user:
                return jsonify({'message': 'User not found'}), 401

            # Check if user role is allowed
            if user['role'] not in roles:
                return jsonify({'message': 'Unauthorized'}), 403

            # Create current_user object
            current_user = {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', ''),
                'role': user['role']
            }

            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator
