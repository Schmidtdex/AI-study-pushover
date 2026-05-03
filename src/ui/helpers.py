import re
import unicodedata
from typing import Optional

from src.repositories import subjects as subjects_repo


def normalize_subject_name(name: str) -> str:
    name = " ".join(name.split())
    name = name.lower()
    name = re.sub(r'\bi\b', '1', name)
    name = re.sub(r'\bii\b', '2', name)
    name = re.sub(r'\biii\b', '3', name)
    name = re.sub(r'\biv\b', '4', name)
    name = re.sub(r'\bv\b', '5', name)
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    return name


def find_existing_subject(typed_name: str) -> Optional[dict]:
    if not typed_name or not typed_name.strip():
        return None

    normalized_input = normalize_subject_name(typed_name)
    if not normalized_input:
        return None

    all_subjects = subjects_repo.list_all()
    for subj in all_subjects:
        if normalize_subject_name(subj["name"]) == normalized_input:
            return subj
    return None