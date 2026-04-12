from app.utils.normalization import normalize_text


def test_normalize_text_unescapes_html_entities():
    assert normalize_text("JoJo&#x27;s Bizarre Adventure: Diamond&nbsp;Is&nbsp;Unbreakable") == "JoJo's Bizarre Adventure: Diamond\xa0Is\xa0Unbreakable"

