from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/incoming-call")
async def incoming_call(request: Request):
    form = await request.form()

    call_sid = form.get("CallSid")
    caller = form.get("From")

    return {
        "call_id": call_sid,
        "caller": caller,
        "action": "ask",
        "message": "Welcome. Please state your reason for calling."
    }