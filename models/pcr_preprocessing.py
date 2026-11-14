import re
import html

def remove_upper_case(text):
    sentences = str(text).split("\n")
    return "\n".join(
        " ".join(word.title() if word.isupper() else word for word in sentence.split())
        for sentence in sentences
    )

def remove_url(text):
    return re.sub(r"https?://\S+|www\.\S+", " ", str(text), flags=re.IGNORECASE)

def remove_html(text):
    return re.sub(r"<[^>]*>", " ", html.unescape(str(text)))

def remove_emoji(text):
    return re.sub(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        " ", str(text)
    )

def normalize_whitespace(text):
    return re.sub(r"\s+", " ", str(text)).strip()

def clean_text(text):
    return normalize_whitespace(remove_emoji(remove_html(remove_url(remove_upper_case(text)))))
