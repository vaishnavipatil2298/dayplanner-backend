from pydantic import BaseModel, Field
from typing import List, Optional, Set
from datetime import datetime, date
from enum import Enum

class CategoryColor(str, Enum):
    RED = "red"
    BLUE = "blue"
    # ... rest of colors ...

class TimeTracking(BaseModel):
    estimated_minutes: int
    actual_minutes: Optional[int] = None
    # ... rest of fields ...

# ... rest of your Pydantic models ...
