from fastapi import APIRouter, Depends
from app.dependencies import get_history

router = APIRouter()

@router.get("/history")
def get_calculation_history(history=Depends(get_history)):
    return list(history)

@router.delete("/history")
def clear_calculation_history(history=Depends(get_history)):
    history.clear()
    return {"message": "History cleared."}
