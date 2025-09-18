import pytest
from app.schemas import ExpressionIn

def test_expression_in():
    expr = ExpressionIn(expr="5 + 10%")
    assert expr.expr == "5 + 10%"

