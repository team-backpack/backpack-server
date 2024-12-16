DEFAULT_LIMIT: int = 3

def get_page(page: int) -> tuple[int]:
    return DEFAULT_LIMIT, DEFAULT_LIMIT * (page - 1)