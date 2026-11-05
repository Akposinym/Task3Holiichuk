from googletrans import Translator, LANGUAGES, LANGCODES

translator = Translator(service_urls=["translate.google.com", "translate.google.co.kr"], raise_exception=True)
translator.client_type = "gtx"


def _normalize(lang: str):
    value = str(lang).strip().lower()
    if value in LANGUAGES:
        return value, LANGUAGES[value].capitalize()
    if value in LANGCODES:
        return LANGCODES[value], value.capitalize()
    return None, None


def CodeLang(lang: str) -> str:
    value = str(lang).strip().lower()
    if value in LANGCODES:
        return LANGCODES[value]
    if value in LANGUAGES:
        return LANGUAGES[value].capitalize()
    return f"Помилка: Мову або код '{lang}' не знайдено."


def _fallback_translate(text: str, dest: str, src: str = "auto"):
    endpoints = (
        "https://translate.googleapis.com/translate_a/t",
        "https://clients5.google.com/translate_a/t",
    )
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Referer": "https://translate.google.com/",
    }
    errors = []

    for endpoint in endpoints:
        try:
            response = translator.client.get(
                endpoint,
                params={"client": "dict-chrome-ex", "sl": src, "tl": dest, "q": text},
                headers=headers,
                timeout=15,
            )
            if response.status_code != 200:
                errors.append(f"{endpoint}: HTTP {response.status_code}")
                continue

            data = response.json()
            if isinstance(data, dict):
                translated = "".join(
                    part.get("trans", "")
                    for part in data.get("sentences", [])
                    if isinstance(part, dict)
                )
                detected = data.get("src") or "auto"
                confidence = data.get("confidence", 0)
            elif isinstance(data, list):
                first = data[0] if data else None
                if isinstance(first, list) and first and isinstance(first[0], str):
                    translated = first[0]
                elif isinstance(first, list):
                    translated = "".join(
                        part[0] for part in first
                        if isinstance(part, list) and part and isinstance(part[0], str)
                    )
                else:
                    translated = ""
                if isinstance(first, list) and len(first) > 1 and isinstance(first[1], str):
                    detected = first[1]
                else:
                    detected = data[2] if len(data) > 2 and isinstance(data[2], str) else "auto"
                confidence = 1
            else:
                translated, detected, confidence = "", "auto", 0

            if translated:
                return translated, detected, confidence
            errors.append(f"{endpoint}: порожня відповідь")
        except Exception as e:
            errors.append(f"{endpoint}: {e}")

    raise RuntimeError("Обидва резервні адреси перекладу не відповіли: " + "; ".join(errors))


def _format_detection(lang, confidence) -> str:
    if isinstance(confidence, (list, tuple)):
        confidence = confidence[0] if confidence else None
    try:
        conf_text = f"{float(confidence):.2f}"
    except (TypeError, ValueError):
        conf_text = "невідомо"
    return f"Мова: {lang}, Confidence: {conf_text}"


def TransLate(text: str, lang: str = "uk") -> str:
    code, _ = _normalize(lang)
    if code is None:
        return f"Помилка: Мову або код '{lang}' не знайдено."

    try:
        return translator.translate(text, dest=code).text
    except Exception as e:
        try:
            translated, _, _ = _fallback_translate(text, code)
            return translated
        except Exception as fallback_error:
            return f"Помилка під час перекладу: {e}; резервний сервіс: {fallback_error}"


def LangDetect(txt: str) -> str:
    try:
        detection = translator.detect(txt)
        return _format_detection(detection.lang, detection.confidence)
    except Exception as e:
        try:
            _, lang, confidence = _fallback_translate(txt, "en", "auto")
            return _format_detection(lang, confidence)
        except Exception as fallback_error:
            return f"Помилка під час визначення мови: {e}; резервний сервіс: {fallback_error}"


if __name__ == "__main__":

    print(f"CodeLang('English') -> {CodeLang('English')}")
    print(f"CodeLang('uk') -> {CodeLang('uk')}")
    print(f"CodeLang('EN') -> {CodeLang('EN')}")
    print(f"CodeLang('unknown') -> {CodeLang('unknown')}")

    sample_text = "The rain in Spain falls mostly on the plain!"
    print(f"Переклад (за замовчуванням, uk): {TransLate(sample_text)}")
    print(f"Переклад (lang='de'): {TransLate(sample_text, lang='de')}")
    print(f"Переклад (lang='French'): {TransLate(sample_text, lang='French')}")

    ua_text = "Що ви там казали?"
    pl_text = "Ja nie znam języka polskiego!"
    print(f"Текст: '{ua_text}' -> {LangDetect(ua_text)}")
    print(f"Текст: '{pl_text}' -> {LangDetect(pl_text)}")