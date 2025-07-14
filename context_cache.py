cache = {}

def save_context(file_id, context):
    cache[file_id] = context

def get_context(file_id):
    return cache.get(file_id, "")