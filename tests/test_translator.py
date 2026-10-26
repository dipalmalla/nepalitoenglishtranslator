from translator import translate_text


def test_translate_text_uses_mymemory_when_available(monkeypatch):
    monkeypatch.setattr('translator._try_mymemory', lambda *args, **kwargs: 'Namaste')
    monkeypatch.setattr('translator._try_libre', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_google_cloud', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_google', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_openai', lambda *args, **kwargs: None)

    result = translate_text('नमस्ते', src='ne', dest='en')

    assert result == 'Namaste'


def test_translate_text_handles_long_queries_by_chunking(monkeypatch):
    seen = []

    class FakeResponse:
        status_code = 200

        def __init__(self, payload):
            self._payload = payload

        def json(self):
            return {'responseData': {'translatedText': self._payload['q']}}

    def fake_get(url, params, timeout):
        seen.append(len(params['q']))
        return FakeResponse(params)

    monkeypatch.setattr('translator.requests.get', fake_get)
    monkeypatch.setattr('translator._try_libre', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_google_cloud', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_google', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_openai', lambda *args, **kwargs: None)

    long_text = ('नमस्ते ' * 300).strip()
    result = translate_text(long_text, src='ne', dest='en')

    assert max(seen) <= 500
    assert result.startswith('नमस्ते')


def test_translate_text_reports_unavailable_when_all_providers_fail(monkeypatch):
    monkeypatch.setattr('translator._try_mymemory', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_libre', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_google_cloud', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_google', lambda *args, **kwargs: None)
    monkeypatch.setattr('translator._try_openai', lambda *args, **kwargs: None)

    result = translate_text('तपाईंलाई नमस्कार', src='ne', dest='en')

    assert result.startswith('[translation-unavailable]')
    assert 'configure' in result.lower()
    assert '[translation-failed]' not in result
