import hashlib
"""Generate hash for a string"""
def generate_hash(data : str):
    return hashlib.sha256(data.encode()).hexdigest()