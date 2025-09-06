# app/Utils/pagination.py

def clamp_limit(limit: int, max_limit: int = 100) -> int:
    return max(1, min(limit, max_limit))
