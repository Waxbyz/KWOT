import html

def text_redactor(text: str) -> str:
    text_unescaped = html.unescape(text)
    text_unescaped = text_unescaped.replace('<br>', '\n')
    text_unescaped = text_unescaped.replace('&quot;', '\"')
    text_unescaped = text_unescaped.replace('&#039;', '\'')

    return text_unescaped