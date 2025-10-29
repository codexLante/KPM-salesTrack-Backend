class CarpoolService:
    
    def __init__(self):
        self.max_passengers = 4
        self.min_gap_minutes = 45
    
    def find_carpool_groups(self, user_meetings):
        
        user_ids = list(user_meetings.keys())
        groups = []
        users_already_grouped = []
        
        # Loop through each user
        for i in range(len(user_ids)):
            user1_id = user_ids[i]
            
            # Skip if already in a group
            if user1_id in users_already_grouped:
                continue

            
            # Start new group
            group = {'users': [user1_id]}
            users_already_grouped.append(user1_id)
            
            # Try to find carpoolers
            for j in range(i + 1, len(user_ids)):
                user2_id = user_ids[j]
                
                if user2_id in users_already_grouped:
                    continue
                
                # Check if compatible
                user1_meetings = user_meetings[user1_id]
                user2_meetings = user_meetings[user2_id]
                can_share = self.can_carpool_together(user1_meetings, user2_meetings)
                
                if can_share == True:
                    group['users'].append(user2_id)
                    users_already_grouped.append(user2_id)
                    
                    # Max 4 people
                    if len(group['users']) >= self.max_passengers:
                        break
            
            groups.append(group)
        
        return groups
    
    def can_carpool_together(self, meetings1, meetings2):
        # Get all meeting times
        all_times = []
        for meeting in meetings1:
            all_times.append(meeting.scheduled_time)
        for meeting in meetings2:
            all_times.append(meeting.scheduled_time)
        
        # Sort times
        all_times.sort()
        
        # Check gaps
        for i in range(len(all_times) - 1):
            time1 = all_times[i]
            time2 = all_times[i + 1]
            
            time_diff = time2 - time1
            minutes = time_diff.total_seconds() / 60
            
            if minutes < self.min_gap_minutes:
                return False
        
        return True