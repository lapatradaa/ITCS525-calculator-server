import re, unicodedata, math
from collections import deque
from datetime import datetime, timezone
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter
from app.dependencies import expand_percent
from app.schema import ExpressionIn as Expression, ExpressionOut as CalculatorLog
from app.routers import calculator, history

HISTORY_MAX = 1000
calc_history = deque(maxlen=HISTORY_MAX)

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(calculator.router, prefix="/calculator", tags=["calculator"])
app.include_router(history.router, prefix="/history", tags=["history"])

# safe evaluator (+ constants)
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})


# --- small helpers (keep it simple) -----------------------------------------
def _normalize_ops(s: str) -> str:
    # make sure unicode operators work: × ÷ − -> * / -
    s = unicodedata.normalize("NFKC", s)
    return s.replace("×", "*").replace("÷", "/").replace("−", "-")


def _implicit_mult_after_paren(s: str) -> str:
    # turns ")9" into ")*9"  and ")(" into ")*("
    return re.sub(r"\)\s*(?=[0-9(])", ")*", s)


# --- endpoints ---------------------------------------------------------------
# Updated endpoint to accept a Pydantic model for proper validation
@app.post("/calculate")
def calculate(expression: Expression):
    expr = expression.expr
    try:
        # 1) normalize pretty ops
        expr = _normalize_ops(expr)
        # Added check for invalid consecutive plus signs
        if "++" in expr:
            raise ValueError("Invalid expression")
        
        # 2) expand percent to (.../100)
        code = expand_percent(expr)

        # 3) support "(99/100)9" -> "(99/100)*9"
        code = _implicit_mult_after_paren(code)

        # evaluate
        result = aeval(code)
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            calc_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "expr": expr,
                "result": "",
                "error": msg,
            })
            return {"ok": False, "expr": expr, "result": "", "error": msg}

        calc_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "expr": expr,
            "result": result,
        })
        return {"ok": True, "expr": expr, "result": result, "error": ""}

    except Exception as e:
        calc_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "expr": expr,
            "result": "",
            "error": str(e),
        })
        return {"ok": False, "expr": expr, "result": "", "error": str(e)}

@app.get("/history")
def get_history(n: int = None):
    """Get the last n history entries, or all if n is None."""
    if n is not None and n > 0:
        return list(calc_history)[-n:]
    return list(calc_history)

@app.delete("/history")
def clear_history():
    calc_history.clear()
    return {"ok": True, "cleared": True}
