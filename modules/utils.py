import os
import hashlib
from datetime import datetime, timedelta

IMAGE_ROOT = "images/slip_images"  # base folder for saving images

def file_hash(uploaded_file):
    # calculate a hash of the uploaded file content (bytes)
    file_bytes = uploaded_file.getvalue()
    return hashlib.md5(file_bytes).hexdigest()

def save_image_and_hash(uploaded_file, folder, filename):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Optionally, save hash for duplicate detection alongside the file
    hash_val = file_hash(uploaded_file)
    with open(os.path.join(folder, f"{filename}.hash"), "w") as fhash:
        fhash.write(hash_val)

def is_duplicate_image(hash_val, folder):
    if not os.path.exists(folder):
        return False
    for file in os.listdir(folder):
        if file.endswith(".hash"):
            with open(os.path.join(folder, file), "r") as f:
                existing_hash = f.read()
                if existing_hash == hash_val:
                    return True
    return False

def calculate_commission(slip_qty, slip_type):
    # Example commission calculation logic
    if slip_type == "Cash Slip":
        return slip_qty * 10  # e.g., 10 currency units per cash slip
    elif slip_type == "Online Slip":
        return slip_qty * 15
    return 0

def generate_weeks(num_weeks=12):
    # Generate a list of (start_date, end_date) tuples for last num_weeks weeks
    weeks = []
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday this week
    for i in range(num_weeks):
        start = start_of_week - timedelta(weeks=i)
        end = start + timedelta(days=6)
        weeks.append((start, end))
    weeks.reverse()
    return weeks
