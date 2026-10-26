import json
import os
import re
from typing import Dict


def load_mapping() -> Dict[str, str]:
    """Load mapping from `preeti_map.json` if present, else use a small built-in map.
    You can provide a full mapping file in the workspace for better accuracy.
    """
    path = os.path.join(os.getcwd(), 'preeti_map.json')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    # small default mapping (incomplete - replace with a full mapping file for production)
    return {
        'cf': 'क',
        'k': 'क',
        'g': 'ग',
        'G': 'घ',
        'a': 'अ',
        'A': 'आ',
        'o;': 'ो',
        'f': 'फ',
        's': 'स',
        'S': 'श',
        '=': 'ा',
        '\\': '्',
        'M': 'ं',
    }


_PREETI_MAP = load_mapping()

# Common romanized / Google-input Nepali words. This gives a practical best-effort
# normalization for mixed real-world documents that contain Latin keyboard input.
_ROMANIZED_WORD_MAP = {
    'namaste': 'नमस्ते',
    'namaskar': 'नमस्कार',
    'namaskaar': 'नमस्कार',
    'kathmandu': 'काठमाडौं',
    'nepal': 'नेपाल',
    'nepali': 'नेपाली',
    'hami': 'हामी',
    'hamro': 'हाम्रो',
    'mero': 'मेरो',
    'ma': 'म',
    'aaja': 'आज',
    'ajhai': 'अझै',
    'sabai': 'सबै',
    'dherai': 'धेरै',
    'ramro': 'राम्रो',
    'ghara': 'घर',
    'ghar': 'घर',
    'bhane': 'भने',
    'timro': 'तिम्रो',
    'timi': 'तिमी',
    'tara': 'तर',
    'kasto': 'कस्तो',
    'kasa': 'कस',
    'naam': 'नाम',
    'chha': 'छ',
    'chhae': 'छ',
    'sanga': 'सँग',
    'prashansa': 'प्रशंसा',
    'sadhai': 'सधै',
    'bhanda': 'भन्दा',
    'safai': 'सफाइ',
    'sau': 'सौ',
    'khabar': 'खबर',
    'sama': 'सम',
    'khoj': 'खोज',
    'ko': 'को',
    'lai': 'लाई',
    'garnu': 'गर्नु',
    'char': 'चर',
    'chha': 'छ',
}


def preeti_to_unicode(text: str) -> str:
    """Convert Preeti-encoded text to Unicode using a simple replacement strategy.

    Note: Preeti is context-sensitive and some mappings require multi-character rules;
    for best results provide a comprehensive `preeti_map.json` mapping file.
    """
    out = text
    # Replace longer keys first to avoid partial overlaps
    for k in sorted(_PREETI_MAP.keys(), key=len, reverse=True):
        out = out.replace(k, _PREETI_MAP[k])
    return out


def _normalize_roman_word(word: str) -> str:
    """Best-effort romanized Nepali normalization for common words and mixed-script text."""
    if not word:
        return word
    key = word.strip().lower()
    if key in _ROMANIZED_WORD_MAP:
        return _ROMANIZED_WORD_MAP[key]

    # Common fallback transliteration for frequently used patterns.
    patterns = [
        ('aa', 'आ'), ('ai', 'ऐ'), ('au', 'औ'), ('kh', 'ख'), ('chh', 'छ'), ('gh', 'घ'),
        ('jh', 'झ'), ('th', 'थ'), ('dh', 'ध'), ('bh', 'भ'), ('sh', 'श'), ('ch', 'च'),
        ('ph', 'फ'), ('dh', 'ध'), ('kh', 'ख'), ('ng', 'ङ'), ('ny', 'ञ'), ('hr', 'ह्र'),
        ('k', 'क'), ('g', 'ग'), ('c', 'च'), ('j', 'ज'), ('t', 'त'), ('d', 'द'), ('p', 'प'),
        ('b', 'ब'), ('m', 'म'), ('y', 'य'), ('r', 'र'), ('l', 'ल'), ('v', 'व'), ('s', 'स'),
        ('h', 'ह'), ('n', 'न'), ('a', 'अ'), ('i', 'इ'), ('u', 'उ'), ('e', 'े'), ('o', 'ो')
    ]
    result = ''
    idx = 0
    while idx < len(word):
        match = None
        for pat, repl in sorted(patterns, key=lambda x: len(x[0]), reverse=True):
            if word[idx:].lower().startswith(pat):
                match = (pat, repl)
                break
        if match is None:
            result += word[idx]
            idx += 1
            continue
        pat, repl = match
        result += repl
        idx += len(pat)
    return result


def normalize_nepali_text(text: str) -> str:
    """Convert mixed Nepali text into a consistent Devanagari form.

    This handles legacy Preeti plus common Romanized/Google-input Nepali spellings.
    """
    if not text:
        return text

    def replace_token(token: str) -> str:
        if not token:
            return token
        if re.search(r'[\u0900-\u097F]', token):
            return token
        if re.search(r'[A-Za-z]', token):
            # Romanized words go through the Nepali transliteration map; short legacy
            # Preeti fragments like 'cf' or 'k' are handled by the Preeti mapper instead.
            if len(token) <= 3 and not any(ch in token.lower() for ch in 'aeiou'):
                return preeti_to_unicode(token)
            pieces = re.split(r'([A-Za-z]+)', token)
            normalized = []
            for piece in pieces:
                if piece and re.search(r'[A-Za-z]', piece):
                    normalized.append(_normalize_roman_word(piece))
                else:
                    normalized.append(piece)
            return ''.join(normalized)
        if token and re.search(r'[a-zA-Z]', token):
            return preeti_to_unicode(token)
        return token

    return ''.join(replace_token(part) for part in re.split(r'(\s+|[^\w\u0900-\u097F]+)', text))


def detect_preeti(text: str) -> bool:
    """Heuristic: if the text contains more ASCII letters than Devanagari letters,
    assume it's typed in a legacy font like Preeti.
    """
    if not text:
        return False
    ascii_letters = sum(1 for ch in text if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z')
    devanagari = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    # If there are no Devanagari chars and some ASCII, likely Preeti
    if devanagari == 0 and ascii_letters > 0:
        return True
    # Otherwise compare ratios
    return ascii_letters > devanagari

