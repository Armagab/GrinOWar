def is_valid_text_length(joke_text: str, max_length: int = 64) -> bool:
    return max_length >= len(joke_text.strip()) > 0