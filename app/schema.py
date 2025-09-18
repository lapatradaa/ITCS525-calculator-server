import re
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class BaseExpression(BaseModel):
    expr: str


class ExpressionIn(BaseExpression):
    pass


class ExpressionOut(ExpressionIn):
    result: Any
    timestamp: str = datetime.now().isoformat()
    error: str = ""


# CalculatorLog is now a subclass of ExpressionOut, removing redundancy
class CalculatorLog(ExpressionOut):
    pass
