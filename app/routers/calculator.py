from fastapi import APIRouter, Depends
from asteval import Interpreter
import math
from app.dependencies import expand_percent, get_history
from app.schema import ExpressionIn, ExpressionOut
from datetime import datetime, timezone

router = APIRouter()

aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})

@router.post("/calculate", response_model=ExpressionOut)
def calculate(expr_in: ExpressionIn, history=Depends(get_history)):
    expr = expr_in.expr
    try:
        code = expand_percent(expr)
        result = aeval(code)
        error = ""
        if aeval.error:
            error = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            result = ""
        log = ExpressionOut(
            expr=expr,
            result=result,
            timestamp=datetime.now(timezone.utc).isoformat(),
            error=error
        )
        history.append(log.dict())
        return log
    except Exception as e:
        log = ExpressionOut(
            expr=expr,
            result="",
            timestamp=datetime.now(timezone.utc).isoformat(),
            error=str(e)
        )
        history.append(log.dict())
        return log


from fastapi import APIRouter, Depends
from app.dependencies import get_history

router = APIRouter()

@router.get("/history")
def get_history_route(n: int = None, history=Depends(get_history)):
    if n is not None and n > 0:
        return list(history)[-n:]
    return list(history)

@router.delete("/history")
def clear_history_route(history=Depends(get_history)):
    history.clear()
    return {"ok": True, "cleared": True}

