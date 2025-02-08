import math
import traceback
from ...constants import (
    DAY_LENGTH, SEASON_LENGTH, TIME_SCALE,
    SEASON_ORDER, SEASONS, TIME_SPEEDS
)

class TimeSystem:
    def __init__(self):
        """Initialize time system"""
        try:
            # Time tracking
            self.time = 0.0  # Total time elapsed
            self.day = 0  # Current day
            self.hour = 0  # Current hour (0-23)
            self.minute = 0  # Current minute (0-59)
            self.day_progress = 0.0  # Progress through current day (0-1)
            
            # Season tracking
            self.season = 0  # Current season index
            self.season_day = 0  # Day within current season
            self.season_progress = 0.0  # Progress through current season (0-1)
            
            # Time control
            self.paused = False
            self.speed = TIME_SPEEDS['normal']
            self.last_update = 0.0
            
        except Exception as e:
            print(f"Error initializing time system: {e}")
            traceback.print_exc()
            
    def update(self, dt: float):
        """Update time system"""
        try:
            if self.paused:
                return
                
            # Update total time with speed multiplier
            time_delta = dt * self.speed * TIME_SCALE
            self.time += time_delta
            
            # Calculate day and time of day
            total_days = self.time / DAY_LENGTH
            self.day = int(total_days)
            
            # Calculate hours and minutes (24-hour format)
            time_of_day = (total_days % 1.0) * 24.0  # Convert to hours
            self.hour = int(time_of_day)
            self.minute = int((time_of_day % 1.0) * 60)
            
            # Update day progress (0-1)
            self.day_progress = time_of_day / 24.0
            
            # Update season progress
            days_per_season = SEASON_LENGTH
            self.season_day = self.day % days_per_season
            self.season_progress = self.season_day / days_per_season
            
            # Update season if needed
            season_index = (self.day // days_per_season) % len(SEASON_ORDER)
            if self.season != season_index:
                self.season = season_index
                
        except Exception as e:
            print(f"Error updating time: {e}")
            traceback.print_exc()
            
    def get_current_season(self) -> str:
        """Get current season name"""
        return SEASON_ORDER[self.season]
        
    def get_time_of_day(self) -> float:
        """Get normalized time of day (0-1)"""
        return self.day_progress
        
    def get_light_level(self) -> float:
        """Calculate light level based on time of day"""
        try:
            # Sunrise at 0.25 (6:00), sunset at 0.75 (18:00)
            if 0.25 <= self.day_progress < 0.75:  # Daytime
                return 1.0
            else:  # Night
                # Smoother transition between day and night
                if self.day_progress < 0.25:  # Dawn
                    return 0.3 + (self.day_progress / 0.25) * 0.7
                else:  # Dusk
                    return 0.3 + ((1.0 - self.day_progress) / 0.25) * 0.7
                    
        except Exception as e:
            print(f"Error calculating light level: {e}")
            traceback.print_exc()
            return 1.0  # Default to full light on error
            
    def set_speed(self, speed_name: str):
        """Set time speed by name"""
        if speed_name in TIME_SPEEDS:
            self.speed = TIME_SPEEDS[speed_name]
            
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        
    def get_state(self) -> dict:
        """Get current state for saving"""
        return {
            'time': self.time,
            'day': self.day,
            'hour': self.hour,
            'minute': self.minute,
            'season': self.season,
            'season_day': self.season_day,
            'paused': self.paused,
            'speed': self.speed
        }
        
    def load_state(self, state: dict):
        """Load state from saved data"""
        try:
            self.time = state.get('time', 0.0)
            self.day = state.get('day', 0)
            self.hour = state.get('hour', 0)
            self.minute = state.get('minute', 0)
            self.season = state.get('season', 0)
            self.season_day = state.get('season_day', 0)
            self.paused = state.get('paused', False)
            self.speed = state.get('speed', TIME_SPEEDS['normal'])
            
        except Exception as e:
            print(f"Error loading time system state: {e}")
            traceback.print_exc() 