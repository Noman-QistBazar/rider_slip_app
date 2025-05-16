import hashlib
import os
from datetime import datetime, timedelta

# Root folder for images (make sure this exists or create it dynamically)
IMAGE_ROOT = "images/slip_images"

def file_hash(file_obj):
    """Generate md5 hash for an uploaded file."""
    file_obj.seek(0)
    file_bytes = file_obj.read()
    file_obj.seek(0)
    return hashlib.md5(file_bytes).hexdigest()

def save_image_and_hash(file_obj, folder, filename):
    """Save uploaded file to disk."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, "wb") as f:
        f.write(file_obj.read())
    file_obj.seek(0)
    # Optionally, save the hash to a file or DB if needed
    return filepath

def is_duplicate_image(hash_val, folder):
    """Check if image hash already exists in folder (checks .hash files)."""
    if not os.path.exists(folder):
        return False
    for fname in os.listdir(folder):
        if fname.endswith(".hash"):
            hash_path = os.path.join(folder, fname)
            with open(hash_path, "r") as f:
                existing_hash = f.read()
            if existing_hash == hash_val:
                return True
    return False

def save_hash_file(hash_val, folder, filename):
    """Save hash to a .hash file for duplicate detection."""
    os.makedirs(folder, exist_ok=True)
    hash_path = os.path.join(folder, f"{filename}.hash")
    with open(hash_path, "w") as f:
        f.write(hash_val)

def calculate_commission(slip_qty, slip_type):
    """Simple commission logic."""
    rate = 10 if slip_type == "Cash Slip" else 15
    return slip_qty * rate

def generate_weeks(num_weeks=4):
    """Generate list of (start_date, end_date) for past weeks."""
    today = datetime.today()
    weeks = []
    for i in range(num_weeks):
        end = today - timedelta(days=today.weekday() + 7 * i)
        start = end - timedelta(days=6)
        weeks.append((start, end))
    weeks.reverse()  # Oldest first
    return weeks
