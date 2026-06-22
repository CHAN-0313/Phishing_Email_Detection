import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    "verify", "urgent", "password", "click", "bank", "account", "login", "confirm", "update", "alert"
]

SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "shorturl.at", "ow.ly"]

URL_REGEX = re.compile(r"https?://[^\s]+", re.IGNORECASE)
IP_IN_URL = re.compile(r"https?://(?:\d{1,3}\.){3}\d{1,3}")


def extract_urls(text: str):
    return URL_REGEX.findall(text or "")


def count_shortened(urls):
    cnt = 0
    for u in urls:
        try:
            host = urlparse(u).netloc.lower()
        except Exception:
            host = u.lower()
        for s in SHORTENERS:
            if s in host:
                cnt += 1
                break
    return cnt


def count_ip_urls(text: str):
    return len(IP_IN_URL.findall(text or ""))


def count_suspicious_keywords(text: str):
    t = (text or "").lower()
    return sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in t)


def count_special_characters(text: str):
    if not text:
        return 0
    return sum(1 for c in text if not c.isalnum() and not c.isspace())


def sender_domain(sender: str):
    if not sender or "@" not in sender:
        return ""
    return sender.split("@", 1)[1].lower()


def domain_reputation(domain: str):
    # Simple heuristic: treat common providers as trusted, others as neutral
    trusted = ["gmail.com", "outlook.com", "hotmail.com", "yahoo.com"]
    if not domain:
        return 0.5
    if any(t in domain for t in trusted):
        return 0.9
    # if domain contains suspicious words
    if any(s in domain for s in ["secure", "support", "bank", "account"]):
        return 0.2
    return 0.5


def extract_features(subject: str, sender: str, content: str):
    text = (subject or "") + "\n" + (content or "")
    urls = extract_urls(text)
    features = {
        "url_count": len(urls),
        "shortened_count": count_shortened(urls),
        "ip_in_url_count": count_ip_urls(text),
        "suspicious_keywords": count_suspicious_keywords(text),
        "special_char_count": count_special_characters(text),
        "email_length": len(text),
        "sender_domain": sender_domain(sender),
        "sender_reputation": domain_reputation(sender_domain(sender)),
        "links_in_text": len(urls),
    }
    return features
