import html

def text_redactor(text: str) -> str:
    text_unescaped = html.unescape(text)
    text_unescaped = text_unescaped.replace('<br>', '\n')

    return text_unescaped