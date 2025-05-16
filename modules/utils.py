import os
import hashlib
from datetime import datetime, timedelta
from typing import Tuple, List
from PIL import Image
import io
import streamlit as st
from supabase_client import get_supabase

def calculate_commission(slip_type: str, quantity: int) -> float:
    """Calculate commission based on slip type and quantity"""
    rates = {
        "Cash Slip": 25,
        "Online Slip": 50
    }
    return rates.get(slip_type, 0) * quantity

def generate_week_ranges(weeks: int = 12) -> List[Tuple[str, Tuple[datetime, datetime]]]:
    """Generate weekly date ranges for the last N weeks"""
    today = datetime.today()
    week_starts = [today - timedelta(days=today.weekday() + i*7) for i in range(weeks)]
    return [
        (f"{start.date()} to {(start + timedelta(days=6)).date()}", (start, start + timedelta(days=6)))
        for start in week_starts
    ]

def save_uploaded_image(file, branch_code: str, rider_name: str) -> str:
    """Save uploaded image with hash verification"""
    supabase = get_supabase()
    file_bytes = file.getvalue()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # Check for duplicates
    res = supabase.table('slips').select('image_hash').eq('image_hash', file_hash).execute()
    if len(res.data) > 0:
        raise ValueError("Duplicate image detected")
    
    # Save to storage
    file_ext = os.path.splitext(file.name)[1]
    file_name = f"{datetime.now().timestamp()}{file_ext}"
    file_path = f"{branch_code}/{rider_name}/{file_name}"
    
    try:
        # For images, we can validate them
        if file_ext.lower() in ['.jpg', '.jpeg', '.png']:
            Image.open(io.BytesIO(file_bytes))
        
        supabase.storage().from_('slip_images').upload(file_path, file_bytes)
        return file_path
    except Exception as e:
        raise ValueError(f"Failed to save image: {str(e)}")

def validate_transaction_id(slip_type: str, transaction_id: str) -> bool:
    """Validate transaction ID based on slip type"""
    if not transaction_id:
        return False
    if slip_type == "Online Slip":
        return len(transaction_id) >= 8 and transaction_id.isdigit()
    return True
