import re

def clean_markdown(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"\n?\d+\.\s*", "\n", text)
    text = re.sub(r"\n?[-•]\s*", "\n", text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    return text.strip()

def get_unique_filenames(documents):
    seen = set()
    unique_files = []
    for doc in documents:
        fname = doc["filename"]
        if fname not in seen:
            seen.add(fname)
            unique_files.append(fname)
    return unique_files
