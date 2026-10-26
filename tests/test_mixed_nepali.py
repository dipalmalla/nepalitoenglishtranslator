from preeti import normalize_nepali_text


def test_mixed_nepali_text_is_normalized_before_translation():
    text = "namaste, kathmandu ma hami"

    normalized = normalize_nepali_text(text)

    assert "नमस्ते" in normalized
    assert "काठमाडौं" in normalized
    assert "हामी" in normalized


def test_common_romanized_nepali_words_are_normalized():
    text = "sabai dherai ramro hamro ghar timro naam kasto chha"

    normalized = normalize_nepali_text(text)

    assert "सबै" in normalized
    assert "धेरै" in normalized
    assert "राम्रो" in normalized or "राम्रों" in normalized
    assert "हाम्रो" in normalized
    assert "घर" in normalized
    assert "तिम्रो" in normalized
    assert "नाम" in normalized
    assert "कस्तो" in normalized
    assert "छ" in normalized
