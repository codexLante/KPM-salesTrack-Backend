from datetime import timedelta
def daterange(start, end):
    dates = []
    while start <= end:
        dates.append(start)
        start += timedelta(days=1)
    return dates


def format_route(route):
    info = {
        'id': route.id,
        'user_id': route.user_id,
        'user_name': route.user.name if route.user else None,
        'route_date': route.route_date.isoformat(),
        'route_type': route.route_type,
        'departure_time': route.scheduled_departure_time.strftime('%H:%M') if route.scheduled_departure_time else None,
        'return_time': route.scheduled_return_time.strftime('%H:%M') if route.scheduled_return_time else None,
        'total_distance_km': round(route.google_route.total_distance_meters / 1000, 2) if route.google_route else None,
        'total_duration_minutes': round(route.google_route.total_duration_seconds / 60, 2) if route.google_route else None,
        'status': route.status,
        'stops_count': len(route.stops) if route.stops else 0
    }

    if route.route_type == 'shared':
        if route.lead_route_id is None:
            info['carpool_role'] = 'lead'
            info['carpoolers'] = [r.user.name for r in route.carpoolers] if route.carpoolers else []
        else:
            info['carpool_role'] = 'passenger'
            info['lead_user'] = route.lead_route.user.name if route.lead_route else None

    return info
def format_stop(stop):
    info = {
        'stop_order': stop.stop_order,
        'stop_type': stop.stop_type,
        'arrival_time': stop.estimated_arrival_time.strftime('%H:%M') if stop.estimated_arrival_time else None,
        'departure_time': stop.estimated_departure_time.strftime('%H:%M') if stop.estimated_departure_time else None,
        'distance_from_previous_km': round(stop.distance_from_previous_meters / 1000, 2) if stop.distance_from_previous_meters else 0,
        'duration_from_previous_minutes': round(stop.duration_from_previous_seconds / 60, 2) if stop.duration_from_previous_seconds else 0,
        'status': stop.status
    }

    if stop.stop_type == 'meeting' and stop.meeting:
        info['meeting'] = {
            'id': stop.meeting.id,
            'client_name': stop.meeting.client_name,
            'location_name': stop.meeting.location.get('label', 'Unknown'),
            'duration': stop.meeting.duration
        }

    return info

def format_google_route(google_route):
    return {
        'total_distance_km': round(google_route.total_distance_meters / 1000, 2),
        'total_duration_minutes': round(google_route.total_duration_seconds / 60, 2),
        'polyline': google_route.encoded_polyline
    }

def format_carpool(route):
    if route.lead_route_id is None:
        return {
            'role': 'lead',
            'carpoolers': [
                {'user_id': r.user_id, 'user_name': r.user.name if r.user else None}
                for r in route.carpoolers
            ]
        }
    else:
        return {
            'role': 'passenger',
            'lead_user_id': route.lead_route.user_id if route.lead_route else None,
            'lead_user_name': route.lead_route.user.name if route.lead_route and route.lead_route.user else None
        }

def format_time(dt):
    return dt.strftime('%H:%M') if dt else None
   
def format_stop_basic(stop):
    info = {
        'stop_order': stop.stop_order,
        'stop_type': stop.stop_type,
        'arrival_time': format_time(stop.estimated_arrival_time),
        'departure_time': format_time(stop.estimated_departure_time)
    }

    if stop.stop_type == 'meeting' and stop.meeting:
        info['meeting'] = {
            'client_name': stop.meeting.client_name,
            'location_name': stop.meeting.location.get('label', 'Unknown')
        }

    return info
