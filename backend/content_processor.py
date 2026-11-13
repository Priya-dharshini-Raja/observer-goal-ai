
def process_content(content: str, chunk_size: int = 500) -> list:
    """
    Split source content into smaller sections
    for analysis by specialized agents.
    """

    if not content or not content.strip():
        return []

    words = content.split()
    chunks = []

    for start in range(0, len(words), chunk_size):
        chunk = " ".join(words[start:start + chunk_size])
        chunks.append(chunk)

    return chunks
