import re
import unicodedata
import math
from collections import deque
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter

from calculator import expand_percent  # expects to turn "10%" -> "(10/100)"

HISTORY_MAX = 1000
history = deque(maxlen=HISTORY_MAX)

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.post("/calculate")
def calculate(expr: str):
    try:
        # 1) normalize pretty ops
        expr = _normalize_ops(expr)

        # 2) expand percent to (.../100)
        code = expand_percent(expr)

        # 3) support "(99/100)9" -> "(99/100)*9"
        code = _implicit_mult_after_paren(code)

        # evaluate
        result = aeval(code)
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "expr": expr,
                "result": "",
                "error": msg,
            })
            return {"ok": False, "expr": expr, "result": "", "error": msg}

        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "expr": expr,
            "result": result,
        })
        return {"ok": True, "expr": expr, "result": result, "error": ""}

    except Exception as e:
        history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "expr": expr,
            "result": "",
            "error": str(e),
        })
        return {"ok": False, "expr": expr, "result": "", "error": str(e)}

#-------------------------------------------------------------------------------------------------------
# TODO GET /hisory
@app.get("/history")
def get_history(n: int = None):
    if n is not None:
        return history[-n:]
    return history

# TODO DELETE /history
@app.delete("/history")
def clear_history():
    history.clear()
    return {"ok": True, "cleared": True}
