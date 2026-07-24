from flask import Flask, request, jsonify, render_template
import urllib.request
import urllib.parse
import json

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Language map – codes compatible with both MyMemory and Google Translate
# ---------------------------------------------------------------------------
LANGUAGES = {
    "af": "Afrikaans", "sq": "Albanian",   "am": "Amharic",
    "ar": "Arabic",    "hy": "Armenian",   "az": "Azerbaijani",
    "eu": "Basque",    "be": "Belarusian", "bn": "Bengali",
    "bs": "Bosnian",   "bg": "Bulgarian",  "ca": "Catalan",
    "ceb":"Cebuano",   "zh": "Chinese (Simplified)", "zh-TW": "Chinese (Traditional)",
    "co": "Corsican",  "hr": "Croatian",   "cs": "Czech",
    "da": "Danish",    "nl": "Dutch",      "en": "English",
    "eo": "Esperanto", "et": "Estonian",   "fi": "Finnish",
    "fr": "French",    "fy": "Frisian",    "gl": "Galician",
    "ka": "Georgian",  "de": "German",     "el": "Greek",
    "gu": "Gujarati",  "ht": "Haitian Creole", "ha": "Hausa",
    "haw":"Hawaiian",  "he": "Hebrew",     "hi": "Hindi",
    "hmn":"Hmong",     "hu": "Hungarian",  "is": "Icelandic",
    "ig": "Igbo",      "id": "Indonesian", "ga": "Irish",
    "it": "Italian",   "ja": "Japanese",   "jv": "Javanese",
    "kn": "Kannada",   "kk": "Kazakh",     "km": "Khmer",
    "rw": "Kinyarwanda","ko":"Korean",     "ku": "Kurdish",
    "ky": "Kyrgyz",    "lo": "Lao",        "la": "Latin",
    "lv": "Latvian",   "lt": "Lithuanian", "lb": "Luxembourgish",
    "mk": "Macedonian","mg":"Malagasy",    "ms": "Malay",
    "ml": "Malayalam", "mt": "Maltese",    "mi": "Maori",
    "mr": "Marathi",   "mn": "Mongolian",  "my": "Myanmar (Burmese)",
    "ne": "Nepali",    "no": "Norwegian",  "ny": "Nyanja (Chichewa)",
    "or": "Odia",      "ps": "Pashto",     "fa": "Persian",
    "pl": "Polish",    "pt": "Portuguese", "pa": "Punjabi",
    "ro": "Romanian",  "ru": "Russian",    "sm": "Samoan",
    "gd": "Scots Gaelic","sr":"Serbian",   "st": "Sesotho",
    "sn": "Shona",     "sd": "Sindhi",     "si": "Sinhala",
    "sk": "Slovak",    "sl": "Slovenian",  "so": "Somali",
    "es": "Spanish",   "su": "Sundanese",  "sw": "Swahili",
    "sv": "Swedish",   "tl": "Tagalog (Filipino)", "tg": "Tajik",
    "ta": "Tamil",     "tt": "Tatar",      "te": "Telugu",
    "th": "Thai",      "tr": "Turkish",    "tk": "Turkmen",
    "uk": "Ukrainian", "ur": "Urdu",       "ug": "Uyghur",
    "uz": "Uzbek",     "vi": "Vietnamese", "cy": "Welsh",
    "xh": "Xhosa",     "yi": "Yiddish",    "yo": "Yoruba",
    "zu": "Zulu",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://translate.google.com/",
}

# ---------------------------------------------------------------------------
# Primary backend: MyMemory (free, no API key, 5 000 words/day)
# Docs: https://mymemory.translated.net/doc/spec.php
# ---------------------------------------------------------------------------
def mymemory_translate(text: str, source: str, target: str) -> dict:
    src = "en" if source == "auto" else source
    langpair = f"{src}|{target}"
    url = (
        "https://api.mymemory.translated.net/get"
        f"?q={urllib.parse.quote(text)}&langpair={urllib.parse.quote(langpair)}"
    )
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if data.get("responseStatus") != 200:
        raise RuntimeError(data.get("responseDetails", "MyMemory error"))

    translated = data["responseData"]["translatedText"]
    # MyMemory sometimes echoes the original on failure
    if translated.upper() == text.upper():
        raise RuntimeError("Translation returned unchanged text")

    return {"translated": translated, "detected_language": None}


# ---------------------------------------------------------------------------
# Fallback: unofficial Google Translate endpoint
# ---------------------------------------------------------------------------
def google_translate(text: str, source: str, target: str) -> dict:
    sl = "auto" if source == "auto" else source
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={urllib.parse.quote(sl)}"
        f"&tl={urllib.parse.quote(target)}"
        f"&dt=t&dt=ld&q={urllib.parse.quote(text)}"
    )
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    parts = [seg[0] for seg in data[0] if seg and seg[0]]
    translated = "".join(parts)

    detected = None
    if source == "auto":
        try:
            detected = data[2]
        except (IndexError, TypeError):
            pass

    return {"translated": translated, "detected_language": detected}


# ---------------------------------------------------------------------------
# Smart translate: try Google first, fall back to MyMemory
# ---------------------------------------------------------------------------
def translate(text: str, source: str, target: str) -> dict:
    errors = []
    for fn in (google_translate, mymemory_translate):
        try:
            return fn(text, source, target)
        except Exception as e:
            errors.append(f"{fn.__name__}: {e}")
    raise RuntimeError(" | ".join(errors))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", languages=LANGUAGES)


@app.route("/translate", methods=["POST"])
def translate_route():
    payload = request.get_json(force=True)
    text   = (payload.get("text") or "").strip()
    source = payload.get("source", "auto")
    target = payload.get("target", "en")

    if not text:
        return jsonify({"error": "No text provided"}), 400
    if target not in LANGUAGES:
        return jsonify({"error": "Invalid target language"}), 400

    try:
        result = translate(text, source, target)
        detected_name = None
        if result.get("detected_language"):
            detected_name = LANGUAGES.get(
                result["detected_language"], result["detected_language"]
            )
        return jsonify({
            "translated":        result["translated"],
            "detected_language": result.get("detected_language"),
            "detected_name":     detected_name,
        })
    except Exception as e:
        return jsonify({"error": f"Translation failed: {e}"}), 500


@app.route("/languages")
def get_languages():
    return jsonify(LANGUAGES)


if __name__ == "__main__":
    print("LinguaShift running -> http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
