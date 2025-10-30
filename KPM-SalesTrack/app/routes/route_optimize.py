from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services import RouteOptimizationService
from app.models import Route, RouteMeeting
from app.db import db
from app.utils import (
    daterange, format_route, format_google_route, format_carpool,
    format_stop, format_stop_basic, format_time,
    admin_required, owner_or_admin_required
)
from flask_jwt_extended import get_jwt_identity, get_jwt

routes_bp = Blueprint('routes', __name__)

OFFICE_LOCATION = {
    'coordinates': [36.8219, -1.30072],
    'label': 'Office'
}


@routes_bp.route('/optimize', methods=['POST'])
@admin_required
def optimize_routes_week():
    try:
        data = request.get_json()
        start_str = data.get('start_date')
        end_str = data.get('end_date')

        if not start_str or not end_str:
            return jsonify({'error': 'Start and end dates are required'}), 400

        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        if start_date > end_date:
            return jsonify({'error': 'Start date must be before or equal to end date'}), 400

        optimizer = RouteOptimizationService(OFFICE_LOCATION)
        all_routes = []

        for day in daterange(start_date, end_date):
            routes = optimizer.optimize_routes_for_date(day)
            for r in routes:
                r.status = 'pending'
                db.session.add(r)
                all_routes.append(format_route(r))

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Created {len(all_routes)} routes from {start_str} to {end_str}',
            'routes': all_routes
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to optimize routes: {str(e)}'}), 500


@routes_bp.route('/<int:route_id>/approve', methods=['PUT'])
@admin_required
def approve_route(route_id):
    try:
        data = request.get_json()
        status = data.get('status')

        if status not in ['accepted', 'rejected']:
            return jsonify({'error': 'Invalid status. Must be "accepted" or "rejected"'}), 400

        route = Route.query.get(route_id)
        if not route:
            return jsonify({'error': 'Route not found'}), 400

        route.status = status
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Route {route_id} marked as {status}'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update route status: {str(e)}'}), 500


@routes_bp.route('/date/<date_str>', methods=['GET'])
@admin_required
def get_routes_by_date(date_str):
    try:
        route_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400
        
        pagination = Route.query.filter_by(route_date=route_date).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        routes_data = [format_route(r) for r in pagination.items]
        
        return jsonify({
            'success': True,
            'date': date_str,
            'routes': routes_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve routes: {str(e)}'}), 500


@routes_bp.route('/<int:route_id>', methods=['GET'])
@owner_or_admin_required
def get_route_details(route_id):
    try:
        route = Route.query.get(route_id)
        if not route:
            return jsonify({'error': 'Route not found'}), 400
        
        current_user_id = int(get_jwt_identity())
        role = get_jwt().get("role")
        
        if role != "admin" and route.user_id != current_user_id:
            return jsonify({'error': 'Access denied. You can only view your own routes.'}), 400

        stops = RouteMeeting.query.filter_by(route_id=route_id).order_by(RouteMeeting.stop_order).all()
        route_data = format_route(route)
        route_data['stops'] = [format_stop(s) for s in stops]

        if route.google_route:
            route_data['google_route'] = format_google_route(route.google_route)

        if route.route_type == 'shared':
            route_data['carpool_info'] = format_carpool(route)

        return jsonify({'success': True, 'route': route_data}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to retrieve route details: {str(e)}'}), 500


@routes_bp.route('/<int:route_id>', methods=['DELETE'])
@admin_required
def delete_route(route_id):
    try:
        route = Route.query.get(route_id)
        if not route:
            return jsonify({'error': 'Route not found'}), 400

        db.session.delete(route)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Route {route_id} deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete route: {str(e)}'}), 500


@routes_bp.route('/user/<int:user_id>/date/<date_str>', methods=['GET'])
@owner_or_admin_required
def get_user_route_by_date(user_id, date_str):
    try:
        current_user_id = int(get_jwt_identity())
        role = get_jwt().get("role")
        
        if role != "admin" and user_id != current_user_id:
            return jsonify({'error': 'Access denied. You can only view your own routes.'}), 400
        
        route_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        route = Route.query.filter_by(
            user_id=user_id,
            route_date=route_date,
            status='accepted'
        ).first()

        if not route:
            return jsonify({
                'success': True,
                'message': 'No accepted route found for this date',
                'route': None
            }), 200

        stops = RouteMeeting.query.filter_by(route_id=route.id).order_by(RouteMeeting.stop_order).all()
        route_data = {
            'id': route.id,
            'route_type': route.route_type,
            'departure_time': format_time(route.scheduled_departure_time),
            'return_time': format_time(route.scheduled_return_time),
            'stops': [format_stop_basic(s) for s in stops]
        }

        return jsonify({'success': True, 'route': route_data}), 200

    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve user route: {str(e)}'}), 500