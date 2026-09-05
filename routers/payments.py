from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.security import get_current_user
from services.payment_service import create_order, verify_payment

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)


class CreateOrderRequest(BaseModel):
    plan_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order")
def api_create_order(
    payload: CreateOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["uid"]
    return create_order(
        user_id=user_id,
        plan_id=payload.plan_id
    )


@router.post("/verify")
def api_verify_payment(
    payload: VerifyPaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["uid"]
    return verify_payment(
        user_id=user_id,
        razorpay_order_id=payload.razorpay_order_id,
        razorpay_payment_id=payload.razorpay_payment_id,
        razorpay_signature=payload.razorpay_signature
    )
