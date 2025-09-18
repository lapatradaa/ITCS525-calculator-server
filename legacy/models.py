from datetime import datetime
from pydantic import BaseModel

class Expression(BaseModel):
    expr: str

class CalculatorLog(BaseModel):
    timestamp: datetime
    expr: str
    result: float