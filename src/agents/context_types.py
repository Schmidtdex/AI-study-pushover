from dataclasses import dataclass, field
from datetime import datetime
from typing import  Optional

@dataclass
class DailyContext:
    today_log: Optional[dict]
    recent_logs: list[dict]
    avg_energy_7d: Optional[float]

@dataclass
class DeadlinesContext:
    upcoming: list[dict]  
    overdue: list[dict]   
    
@dataclass
class SessionsContext:
    recent: list[dict]
    total_by_subject_7d: list[dict]
    topics_status: list[dict]

@dataclass
class TracksContext:
    active: list[dict]

@dataclass
class DerivedContext:
    days_studied_in_last_7: int
    neglected_subjects: list[dict]      
    forgotten_topics: list[dict]        
    urgent_deadlines: list[dict] 

@dataclass
class ContextBundle:
    generated_at: datetime
    daily: DailyContext
    deadlines: DeadlinesContext
    sessions: SessionsContext
    tracks: TracksContext
    derived: DerivedContext
    