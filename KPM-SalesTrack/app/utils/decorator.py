from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if not user_role:
                return jsonify({'error': 'Role information missing from token'}), 401
            
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Access denied',
                    'required_roles': list(allowed_roles),
                    'your_role': user_role
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role != 'admin':
            return jsonify({
                'error': 'Admin access required',
                'your_role': user_role
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def salesman_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role != 'sales':
            return jsonify({
                'error': 'Salesman access required',
                'your_role': user_role
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def sales_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        user_role = claims.get('role')
        
        # Allow both 'sales' and 'admin' roles
        if user_role not in ['sales', 'admin']:
            return jsonify({
                'error': 'Sales access required',
                'your_role': user_role,
                'allowed_roles': ['sales', 'admin']
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def owner_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        current_user_id = int(get_jwt_identity())
        user_role = claims.get('role')
        
        # Admins can access everything
        if user_role == 'admin':
            return fn(*args, **kwargs)
        
        target_user_id = kwargs.get('user_id')
        
        
        if target_user_id is None:
            return fn(*args, **kwargs)
        
        # Check if current user is trying to access their own data
        try:
            if current_user_id == int(target_user_id):
                return fn(*args, **kwargs)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user ID format'}), 400
        

        return jsonify({
            'error': 'Access denied. You can only access your own resources.'
        }), 403
    
    return wrapper