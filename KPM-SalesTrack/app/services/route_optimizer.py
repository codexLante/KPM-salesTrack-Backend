from datetime import datetime
from app.models import Meeting
from app.db import db
from .carpool_service import CarpoolService
from .google_routes_service import GoogleRoutesService
from .route_creator import RouteCreator


class RouteOptimizationService:
    
    def __init__(self, office_location):
        self.office_location = office_location
        self.carpool_service = CarpoolService()
        self.google_service = GoogleRoutesService(office_location)
        self.route_creator = RouteCreator(office_location)
    
    def optimize_routes_for_date(self, date):
        meetings = Meeting.query.filter_by(
            scheduled_date=date,
            meeting_type='field'
        ).all()
        
        if len(meetings) == 0:
            return []
        user_meetings = {}
        for meeting in meetings:
            user_id = meeting.user_id
            if user_id not in user_meetings:
                user_meetings[user_id] = []
            user_meetings[user_id].append(meeting)
    
        carpool_groups = self.carpool_service.find_carpool_groups(user_meetings)
        
        all_routes = []
        
        for group in carpool_groups:
            if len(group['users']) == 1:
                user_id = group['users'][0]
                user_meeting_list = user_meetings[user_id]
                route = self.route_creator.create_individual_route(user_meeting_list)
                
                if route is not None:
                    all_routes.append(route)
            else:
                combined_meetings = []
                for user_id in group['users']:
                    for meeting in user_meetings[user_id]:
                        combined_meetings.append(meeting)
                
                routes = self.route_creator.create_shared_routes(
                    combined_meetings, 
                    group['users']
                )
                
                for route in routes:
                    all_routes.append(route)
        db.session.commit()
        return all_routes
