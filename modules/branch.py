import os
import hashlib
from datetime import datetime

# Constants
DATA_FILE = "data/branch_data.xlsx"  # Path to your Excel data file
IMAGE_HASH_FILE = "data/image_hashes.txt"  # To track image hashes to avoid duplicates

# Calculate SHA256 hash of uploaded file (Streamlit file uploader)
def file_hash(uploaded_file):
    hasher = hashlib.sha256()
    file_bytes = uploaded_file.getbuffer()
    hasher.update(file_bytes)
    return hasher.hexdigest()

# Save uploaded image to disk and record its hash
def save_image_and_hash(uploaded_file, folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Save hash to hash file (optional for checking duplicates)
    hash_val = file_hash(uploaded_file)
    with open(IMAGE_HASH_FILE, "a") as f:
        f.write(hash_val + "\n")

    return file_path

# Check if an image hash already exists in folder (duplicate detection)
def is_duplicate_image(hash_val, folder):
    if not os.path.exists(IMAGE_HASH_FILE):
        return False
    with open(IMAGE_HASH_FILE, "r") as f:
        hashes = f.read().splitlines()
    return hash_val in hashes

# Calculate commission based on slip quantity and type
def calculate_commission(slip_qty, slip_type):
    # Example: Cash slip = 10 per slip, Online slip = 12 per slip
    rates = {"Cash Slip": 10, "Online Slip": 12}
    return slip_qty * rates.get(slip_type, 0)

# Generate weekly date ranges (last 4 weeks as example)
def generate_weeks():
    weeks = []
    today = datetime.today()
    for i in range(4):
        end_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=6)
        weeks.append((start_date, end_date))
        today = start_date - timedelta(days=1)
    return weeks[::-1]  # Return in ascending order

# Backup Excel data file (creates timestamped copy)
def backup_data():
    if os.path.exists(DATA_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"data/backup_{timestamp}.xlsx"
        with open(DATA_FILE, "rb") as original, open(backup_file, "wb") as backup:
            backup.write(original.read())

