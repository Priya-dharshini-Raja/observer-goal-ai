
from content_processor import process_content

sample_text = """
Artificial intelligence analyzes information.
Multi-agent systems divide tasks between agents.
Observer goal modeling prioritizes relevant findings.
"""

chunks = process_content(sample_text, chunk_size=8)

print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"Chunk {index}: {chunk}")
