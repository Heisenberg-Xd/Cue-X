import os
import pandas as pd
from config import UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_session(session_id: str):
    path = os.path.join(UPLOAD_FOLDER, f'session_{session_id}.csv')
    if not os.path.exists(path):
        return None, f"Session {session_id} not found"
    try:
        return pd.read_csv(path), None
    except Exception as e:
        return None, str(e)
