import sys
from googletrans import Translator, LANGUAGES

translator = Translator(service_urls=['translate.googleapis.com'], raise_exception=True)


def CodeLang(lang: str) -> str:
    cleaned_lang = lang.strip().lower()
    if cleaned_lang in LANGUAGES:
        return LANGUAGES[cleaned_lang].capitalize()

    inverted_languages = {name.lower(): code for code, name in LANGUAGES.items()}
    if cleaned_lang in inverted_languages:
        return inverted_languages[cleaned_lang]

    return f"Помилка: Мову або код '{lang}' не знайдено."


def TransLate(text: str, lang: str = "uk") -> str:
    target_lang = lang.strip().lower()

    if target_lang not in LANGUAGES:
        resolved_code = CodeLang(target_lang)

        if resolved_code.startswith("Помилка:"):
            return resolved_code

        target_lang = resolved_code


    try:
        result = translator.translate(text, dest=target_lang)
        return result.text

    except Exception as e:
        return f"Помилка під час перекладу: {e}"


def LangDetect(txt: str) -> str:
    try:
        detection = translator.detect(txt)
        return f"Мова: {detection.lang}, Confidence: {detection.confidence:.2f}"

    except Exception as e:
        return f"Помилка під час визначення мови: {e}"


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