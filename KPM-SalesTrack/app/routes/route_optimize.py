from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from app.services import RouteOptimizationService
from app.models import Route, RouteMeeting
from app.db import db
from app.utils import daterange, format_route,format_google_route,format_carpool,format_stop,format_stop_basic,format_time

routes_bp = Blueprint('routes', __name__)

OFFICE_LOCATION = {
    'coordinates': [36.8219,  -1.30072],  
    'label': 'Office'
}

@routes_bp.route('/optimize', methods=['POST'])
def optimize_routes_week():
    data = request.get_json()
    start_str = data.get('start_date')
    end_str = data.get('end_date')

    if not start_str or not end_str:
        return jsonify({'error': 'Start and end dates are required'}), 400

    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    if start_date > end_date:
        return jsonify({'error': 'Start date must be before end date'}), 400

    try:
        optimizer = RouteOptimizationService(OFFICE_LOCATION)
        all_routes = []

        for day in daterange(start_date, end_date):
            routes = optimizer.optimize_routes_for_date(day)
            all_routes.extend([format_route(r) for r in routes])

        return jsonify({
            'success': True,
            'message': f'Created {len(all_routes)} routes from {start_str} to {end_str}',
            'routes': all_routes
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@routes_bp.route('/date/<date_str>', methods=['GET'])
def get_routes_by_date(date_str):
    try:
        route_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        routes = Route.query.filter_by(route_date=route_date).all()
        routes_data = [format_route(r) for r in routes]

        return jsonify({
            'success': True,
            'date': date_str,
            'routes': routes_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/<int:route_id>', methods=['GET'])
def get_route_details(route_id):
    try:
        route = Route.query.get(route_id)
        if not route:
            return jsonify({'error': 'Route not found'}), 404

        stops = RouteMeeting.query.filter_by(route_id=route_id).order_by(RouteMeeting.stop_order).all()
        route_data = format_route(route)
        route_data['stops'] = [format_stop(s) for s in stops]

        if route.google_route:
            route_data['google_route'] = format_google_route(route.google_route)

        if route.route_type == 'shared':
            route_data['carpool_info'] = format_carpool(route)

        return jsonify({'success': True, 'route': route_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@routes_bp.route('/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    try:
        route = Route.query.get(route_id)
        if not route:
            return jsonify({'error': 'Route not found'}), 404

        db.session.delete(route)
        db.session.commit()

        return jsonify({'success': True, 'message': f'Route {route_id} deleted'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

@routes_bp.route('/user/<int:user_id>/date/<date_str>', methods=['GET'])
def get_user_route_by_date(user_id, date_str):
    try:
        route_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        route = Route.query.filter_by(user_id=user_id, route_date=route_date).first()

        if not route:
            return jsonify({'success': True, 'message': 'No route found', 'route': None}), 200

        stops = RouteMeeting.query.filter_by(route_id=route.id).order_by(RouteMeeting.stop_order).all()
        route_data = {
            'id': route.id,
            'route_type': route.route_type,
            'departure_time': format_time(route.scheduled_departure_time),
            'return_time': format_time(route.scheduled_return_time),
            'stops': [format_stop_basic(s) for s in stops]
        }

        return jsonify({'success': True, 'route': route_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
