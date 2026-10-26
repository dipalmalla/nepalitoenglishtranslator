import os
import re
import requests
import html


def _chunk_text_for_mymemory(text: str, max_chars: int = 450) -> list[str]:
    cleaned = (text or '').strip()
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]

    parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+|\n+', cleaned) if p and p.strip()]
    if not parts:
        return [cleaned]

    chunks = []
    current = ''
    for part in parts:
        if len(current) + (1 if current else 0) + len(part) <= max_chars:
            current = f'{current} {part}'.strip() if current else part
        else:
            if current:
                chunks.append(current)
            if len(part) <= max_chars:
                current = part
            else:
                for idx in range(0, len(part), max_chars):
                    segment = part[idx:idx + max_chars].strip()
                    if segment:
                        chunks.append(segment)
                current = ''
    if current:
        chunks.append(current)
    return [chunk.strip() for chunk in chunks if chunk and chunk.strip()]


def _try_mymemory(text: str, src: str, dest: str) -> str | None:
    try:
        chunks = _chunk_text_for_mymemory(text)
        if not chunks:
            return None

        translated_parts = []
        for chunk in chunks:
            params = {
                'q': chunk,
                'langpair': f'{src}|{dest}',
            }
            resp = requests.get('https://api.mymemory.translated.net/get', params=params, timeout=30)
            if resp.status_code >= 400:
                return None
            data = resp.json()
            if not isinstance(data, dict):
                return None
            translated = data.get('responseData', {}).get('translatedText')
            if not translated:
                return None
            translated_parts.append(translated.strip())

        return ' '.join(part for part in translated_parts if part).strip() or None
    except Exception:
        return None


def _try_libre(text: str, src: str, dest: str) -> str | None:
    url = os.environ.get('LIBRETRANSLATE_URL')
    if not url:
        return None
    try:
        resp = requests.post(url, data={
            'q': text,
            'source': src,
            'target': dest,
            'format': 'text'
        }, timeout=30)
        if resp.status_code >= 400:
            return None
        data = resp.json()
        if isinstance(data, dict) and 'translatedText' in data:
            return data['translatedText']
        if isinstance(data, str):
            return data
    except Exception:
        return None


def _try_google(text: str, src: str, dest: str) -> str | None:
    try:
        params = {
            'client': 'gtx',
            'sl': src,
            'tl': dest,
            'dt': 't',
            'q': text,
        }
        r = requests.get('https://translate.googleapis.com/translate_a/single', params=params, timeout=30)
        if r.status_code >= 400:
            return None
        content_type = (r.headers.get('Content-Type') or '').lower()
        if 'json' not in content_type and 'javascript' not in content_type:
            return None
        arr = r.json()
        if not isinstance(arr, list) or len(arr) < 2 or not isinstance(arr[0], list):
            return None
        segments = arr[0]
        translated = ''.join(segment[0] for segment in segments if segment and len(segment) > 0 and segment[0])
        return html.unescape(translated)
    except Exception:
        return None


def _try_google_cloud(text: str, src: str, dest: str) -> str | None:
    # Uses Google Cloud Translate REST API v2 with API key from env var GOOGLE_API_KEY
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        return None
    try:
        url = 'https://translation.googleapis.com/language/translate/v2'
        payload = {
            'q': text,
            'source': src,
            'target': dest,
            'format': 'text',
            'key': api_key,
        }
        r = requests.post(url, data=payload, timeout=30)
        if r.status_code >= 400:
            return None
        content_type = (r.headers.get('Content-Type') or '').lower()
        if 'json' not in content_type:
            return None
        data = r.json()
        if 'data' in data and 'translations' in data['data'] and len(data['data']['translations']) > 0:
            return data['data']['translations'][0].get('translatedText')
        return None
    except Exception:
        return None


def _try_openai(text: str, src: str, dest: str) -> str | None:
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        return None
    try:
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
        prompt = f"Translate the following text from {src} to {dest}. Return only the translated text.\n\nText:\n{text}"
        body = {
            'model': os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0,
            'max_tokens': 2000,
        }
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code >= 400:
            return None
        content_type = (resp.headers.get('Content-Type') or '').lower()
        if 'json' not in content_type:
            return None
        data = resp.json()
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content'].strip()
    except Exception:
        return None


def translate_text(text: str, src: str = 'ne', dest: str = 'en') -> str:
    for fn in (_try_mymemory, _try_libre, _try_google_cloud, _try_google, _try_openai):
        try:
            out = fn(text, src, dest)
            if out:
                return out
        except Exception:
            continue
    return "[translation-unavailable] No live translation backend is reachable. Configure LIBRETRANSLATE_URL or OPENAI_API_KEY to enable translations."
