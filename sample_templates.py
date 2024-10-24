from typing import List

def load_sample_templates(sample_files: List[str]) -> str | None:
    if not sample_files:
        return None
    return "\n---\n".join([ open(sample_file, 'r').read() for sample_file in sample_files ])
