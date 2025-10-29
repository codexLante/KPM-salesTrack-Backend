from datetime import timedelta
from app.models import RouteMeeting
from app.db import db


class StopCreator:
    
    def create_stops_for_route(self, route, meetings, google_route):

        legs = google_route.raw_response['routes'][0].get('legs', [])
        self.create_start_stop(route, meetings[0])        
        self.create_meeting_stops(route, meetings, legs)
        self.create_end_stop(route, meetings, legs)
    
    def create_start_stop(self, route, first_meeting):

        start_stop = RouteMeeting(
            route_id=route.id,
            meeting_id=first_meeting.id,
            stop_order=0,
            stop_type='start',
            estimated_arrival_time=route.scheduled_departure_time,
            estimated_departure_time=route.scheduled_departure_time,
            distance_from_previous_meters=0,
            duration_from_previous_seconds=0,
            status='scheduled'
        )
        db.session.add(start_stop)
    
    def create_meeting_stops(self, route, meetings, legs):

        current_time = route.scheduled_departure_time
        stop_number = 1
        
        for i in range(len(meetings)):
            meeting = meetings[i]
            leg = legs[i]
            
            duration_str = leg['duration']
            travel_seconds = int(duration_str.replace('s', ''))
            arrival = current_time + timedelta(seconds=travel_seconds)
            departure = arrival + timedelta(minutes=meeting.duration)
            distance = leg['distanceMeters']
            
            stop = RouteMeeting(
                route_id=route.id,
                meeting_id=meeting.id,
                stop_order=stop_number,
                stop_type='meeting',
                estimated_arrival_time=arrival,
                estimated_departure_time=departure,
                distance_from_previous_meters=distance,
                duration_from_previous_seconds=travel_seconds,
                status='scheduled'
            )
            db.session.add(stop)

            current_time = departure
            stop_number = stop_number + 1
    
    def create_end_stop(self, route, meetings, legs):
        if len(legs) <= len(meetings):
            return
        last_meeting = meetings[len(meetings) - 1]
        last_departure = last_meeting.scheduled_time + timedelta(minutes=last_meeting.duration)
        return_leg = legs[len(legs) - 1]
        return_seconds = int(return_leg['duration'].replace('s', ''))
        return_distance = return_leg['distanceMeters']
        
        arrival_at_office = last_departure + timedelta(seconds=return_seconds)
        end_stop = RouteMeeting(
            route_id=route.id,
            meeting_id=last_meeting.id,
            stop_order=len(meetings) + 1,
            stop_type='end',
            estimated_arrival_time=arrival_at_office,
            estimated_departure_time=arrival_at_office,
            distance_from_previous_meters=return_distance,
            duration_from_previous_seconds=return_seconds,
            status='scheduled'
        )
        db.session.add(end_stop)
