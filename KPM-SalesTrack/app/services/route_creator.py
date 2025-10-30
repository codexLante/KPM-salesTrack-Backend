from datetime import timedelta
from app.models import Route
from app.db import db
from .google_routes_service import GoogleRoutesService
from .stop_creator import StopCreator


class RouteCreator:
    
    def __init__(self, office_location):
        self.office_location = office_location
        self.google_service = GoogleRoutesService(office_location)
        self.stop_creator = StopCreator()
        self.buffer_minutes = 15
    
    def create_individual_route(self, meetings):
        if len(meetings) == 0:
            return None
        

        sorted_meetings = sorted(meetings, key=lambda m: m.scheduled_time) 
        
        # Get Google route
        google_route = self.google_service.get_or_create_route(sorted_meetings)
        if google_route is None:
            return None
        
        # Calculate times
        departure = self.calculate_departure_time(sorted_meetings, google_route)
        return_time = self.calculate_return_time(sorted_meetings, google_route)
        
        route = Route(
            user_id=sorted_meetings[0].user_id,
            route_date=sorted_meetings[0].scheduled_date,
            google_route_id=google_route.id,
            route_type='individual',
            scheduled_departure_time=departure,
            scheduled_return_time=return_time,
            status='optimized'
        )
        
        db.session.add(route)
        db.session.commit()
        

        self.stop_creator.create_stops_for_route(route, sorted_meetings, google_route)
        
        return route
    
    def create_shared_routes(self, all_meetings, user_ids):

        if len(all_meetings) == 0:
            return []
        

        sorted_meetings = sorted(all_meetings, key=lambda m: m.scheduled_time)
        

        google_route = self.google_service.get_or_create_route(sorted_meetings)
        if google_route is None:
            return []
        

        departure = self.calculate_departure_time(sorted_meetings, google_route)
        return_time = self.calculate_return_time(sorted_meetings, google_route)
        route_date = sorted_meetings[0].scheduled_date
        
        routes = []
        
        lead_route = Route(
            user_id=user_ids[0],
            route_date=route_date,
            google_route_id=google_route.id,
            route_type='shared',
            lead_route_id=None,
            scheduled_departure_time=departure,
            scheduled_return_time=return_time,
            status='optimized'
        )
        
        db.session.add(lead_route)
        db.session.commit()
        

        self.stop_creator.create_stops_for_route(lead_route, sorted_meetings, google_route)
        routes.append(lead_route)
        

        for i in range(1, len(user_ids)):
            passenger_id = user_ids[i]
            
            user_meetings = []
            for meeting in sorted_meetings:
                if meeting.user_id == passenger_id:
                    user_meetings.append(meeting)
            
            passenger_route = Route(
                user_id=passenger_id,
                route_date=route_date,
                google_route_id=google_route.id,
                route_type='shared',
                lead_route_id=lead_route.id,
                scheduled_departure_time=departure,
                scheduled_return_time=return_time,
                status='optimized'
            )
            
            db.session.add(passenger_route)
            db.session.commit()
            
            self.stop_creator.create_stops_for_route(passenger_route, user_meetings, google_route)
            routes.append(passenger_route)
        
        return routes
    
    def calculate_departure_time(self, meetings, google_route):


        first_meeting = meetings[0]
        for meeting in meetings:
            if meeting.scheduled_time < first_meeting.scheduled_time:
                first_meeting = meeting
        

        legs = google_route.raw_response['routes'][0].get('legs', [])
        if len(legs) == 0:
            return first_meeting.scheduled_time - timedelta(minutes=30)
        
        first_leg = legs[0]
        travel_seconds = int(first_leg['duration'].replace('s', ''))
        buffer_seconds = self.buffer_minutes * 60
        
        total_seconds = travel_seconds + buffer_seconds
        departure = first_meeting.scheduled_time - timedelta(seconds=total_seconds)
        
        return departure
    
    def calculate_return_time(self, meetings, google_route):
        # Find last meeting
        last_meeting = meetings[0]
        for meeting in meetings:
            if meeting.scheduled_time > last_meeting.scheduled_time:
                last_meeting = meeting
        
        # Get return leg
        legs = google_route.raw_response['routes'][0].get('legs', [])
        if len(legs) == 0 or len(legs) <= len(meetings):
            meeting_end = last_meeting.scheduled_time + timedelta(minutes=last_meeting.duration)
            return meeting_end + timedelta(minutes=30)
        
        return_leg = legs[len(legs) - 1]
        return_seconds = int(return_leg['duration'].replace('s', ''))
        
        meeting_end = last_meeting.scheduled_time + timedelta(minutes=last_meeting.duration)
        return_time = meeting_end + timedelta(seconds=return_seconds)
        
        return return_time