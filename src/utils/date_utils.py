import re
from datetime import datetime
from typing import List, Optional, Tuple

def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse various date string formats into datetime object.
    Supports:
    - YYYY.MM
    - YYYY-MM
    - YYYY/MM
    - YYYY年MM月
    - YYYY.MM.DD
    - Present/Now/至今
    """
    if not date_str:
        return None
        
    date_str = date_str.strip()
    
    # Handle "Present" keywords
    if any(keyword in date_str.lower() for keyword in ['present', 'now', 'current', '至今', '目前']):
        return datetime.now()
        
    # Common formats
    formats = [
        "%Y.%m", "%Y-%m", "%Y/%m", "%Y年%m月",
        "%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日",
        "%b %Y", "%B %Y",  # Jan 2020, January 2020
        "%Y" # Just year
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    # Regex fallback for "YYYY.MM" patterns buried in text
    match = re.search(r'(\d{4})[.\-/年](\d{1,2})', date_str)
    if match:
        try:
            year, month = match.groups()
            return datetime(int(year), int(month), 1)
        except:
            pass
            
    return None

def calculate_duration_years(start_date: datetime, end_date: datetime) -> float:
    """Calculate duration in years between two dates."""
    if not start_date or not end_date:
        return 0.0
        
    # Difference in days
    delta = end_date - start_date
    days = delta.days
    
    # Approximate years
    return round(days / 365.25, 2)

def calculate_total_experience(work_experiences: List[dict]) -> float:
    """
    Calculate total years of experience from a list of work experience entries.
    Each entry is expected to have a 'dates' string or 'start_date'/'end_date'.
    """
    if not work_experiences:
        return 0.0
        
    total_years = 0.0
    
    # Simple summation of durations (ignoring overlap for now, or we can merge intervals)
    # Let's try to merge intervals to be more accurate and avoid double counting
    intervals = []
    
    for work in work_experiences:
        # Try to get start/end from pre-parsed fields or parse 'dates' string
        s_date = None
        e_date = None
        
        # Priority 1: Use LLM extracted start/end dates
        if work.get("start_date"):
            s_date = parse_date_string(work.get("start_date"))
        if work.get("end_date"):
            e_date = parse_date_string(work.get("end_date"))
            
        # Priority 2: Parse from 'dates' string if fields missing
        if not s_date or not e_date:
            dates_str = work.get("dates")
            if dates_str:
                # Split usually by "-" or "to" or "至"
                parts = re.split(r'\s*[-–to至]\s*', dates_str)
                if len(parts) >= 2:
                    if not s_date: s_date = parse_date_string(parts[0])
                    if not e_date: e_date = parse_date_string(parts[1])
                elif len(parts) == 1:
                    # Maybe just a start date? Or "2020 - "
                    if not s_date: s_date = parse_date_string(parts[0])
                    # If it looks like a range "2020-"
                    if dates_str.strip().endswith("-") or dates_str.strip().endswith("–"):
                        if not e_date: e_date = datetime.now()
        
        if s_date and e_date:
            if s_date > e_date:
                s_date, e_date = e_date, s_date
            intervals.append((s_date, e_date))
            
    if not intervals:
        return 0.0
        
    # Merge intervals
    intervals.sort(key=lambda x: x[0])
    
    merged = []
    if intervals:
        curr_start, curr_end = intervals[0]
        for next_start, next_end in intervals[1:]:
            if next_start <= curr_end: # Overlap
                curr_end = max(curr_end, next_end)
            else:
                merged.append((curr_start, curr_end))
                curr_start, curr_end = next_start, next_end
        merged.append((curr_start, curr_end))
        
    # Sum merged intervals
    for start, end in merged:
        total_years += calculate_duration_years(start, end)
        
    return round(total_years, 1)
