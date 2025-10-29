import os
import requests
import hashlib
import json
from app.models import GoogleRoute
from app.db import db


class GoogleRoutesService:
    
    def __init__(self, office_location):
        self.office_location = office_location
        self.api_key = os.getenv("GOOGLE_ROUTES_API_KEY")
    
    def get_or_create_route(self, meetings):

        # Create hash for these waypoints
        waypoint_hash = self.create_waypoints_hash(meetings)
        
        # Check if already exists
        existing = GoogleRoute.query.filter_by(waypoints_hash=waypoint_hash).first()
        if existing is not None:
            print(f"Reusing Google route {existing.id}")
            return existing
        

        print("Calling Google Routes API...")
        api_response = self.call_google_api(meetings)
        
        if api_response is None:
            return None
        
        if 'routes' not in api_response or len(api_response['routes']) == 0:
            return None
        
        # Save to database
        return self.save_google_route(api_response, waypoint_hash)
    
    def create_waypoints_hash(self, meetings):

        waypoints = []
        sorted_meetings = sorted(meetings, key=lambda m: m.id)
        
        for meeting in sorted_meetings:
            lat = meeting.location['coordinates'][1]
            lng = meeting.location['coordinates'][0]
            waypoints.append({'lat': lat, 'lng': lng})
        
        waypoint_json = json.dumps(waypoints, sort_keys=True)
        hash_value = hashlib.md5(waypoint_json.encode()).hexdigest()
        return hash_value
    
    def call_google_api(self, meetings):

        office_lat = self.office_location['coordinates'][1]
        office_lng = self.office_location['coordinates'][0]
        
        waypoints = []
        for meeting in meetings:
            lat = meeting.location['coordinates'][1]
            lng = meeting.location['coordinates'][0]
            
            waypoint = {
                'location': {
                    'latLng': {
                        'latitude': lat,
                        'longitude': lng
                    }
                }
            }
            waypoints.append(waypoint)
        
        # Build request
        request_data = {
            'origin': {
                'location': {
                    'latLng': {
                        'latitude': office_lat,
                        'longitude': office_lng
                    }
                }
            },
            'destination': {
                'location': {
                    'latLng': {
                        'latitude': office_lat,
                        'longitude': office_lng
                    }
                }
            },
            'intermediates': waypoints,
            'travelMode': 'DRIVE',
            'routingPreference': 'TRAFFIC_AWARE',
            'computeAlternativeRoutes': False,
            'routeModifiers': {
                'avoidTolls': False,
                'avoidHighways': False,
                'avoidFerries': True
            },
            'languageCode': 'en-US',
            'units': 'METRIC'
        }
        
        try:
            url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.api_key,
                'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs'
            }
            
            response = requests.post(url, headers=headers, json=request_data)
            
            if response.status_code != 200:
                print(f"API error: {response.status_code}")
                return None
            
            return response.json()
            
        except Exception as e:
            print(f"Google API error: {e}")
            return None
    
    def save_google_route(self, api_response, waypoint_hash):

        route_data = api_response['routes'][0]
        
        distance = route_data['distanceMeters']
        duration_str = route_data['duration']
        duration_seconds = int(duration_str.replace('s', ''))
        polyline = route_data['polyline']['encodedPolyline']
        
        google_route = GoogleRoute(
            raw_response=api_response,
            total_distance_meters=distance,
            total_duration_seconds=duration_seconds,
            encoded_polyline=polyline,
            waypoints_hash=waypoint_hash
        )
        
        db.session.add(google_route)
        db.session.commit()
        
        print(f"Created Google route {google_route.id}")
        return google_route