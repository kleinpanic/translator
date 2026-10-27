import argparse
import os
import sys
from deep_translator import GoogleTranslator, MyMemoryTranslator, PonsTranslator
from deep_translator.exceptions import LanguageNotSupportedException
import json

# Bundled default config (shipped next to this script) and the per-user config
# that --provider writes to. The user config must not depend on the current
# working directory, and the install directory may not be writable.
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
CONFIG_FILE = os.path.join(
    os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),
    "translator",
    "config.json",
)

PROVIDERS = {
    "Google": GoogleTranslator,
    "MyMemory": MyMemoryTranslator,
    "Pons": PonsTranslator,
}

# Each provider rejects input of this many characters or more.
MAX_CHARS = {
    "Google": 5000,
    "MyMemory": 500,
    "Pons": 50,
}


class TranslatorError(Exception):
    pass


def load_config():
    for path in (CONFIG_FILE, DEFAULT_CONFIG_FILE):
        if os.path.exists(path):
            with open(path, 'r') as file:
                return json.load(file)
    return {"provider": "Google"}  # Default provider

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

def get_translator(provider, source_language='auto', target_language='en'):
    if provider not in PROVIDERS:
        raise TranslatorError(
            f"Provider '{provider}' is not supported. Choose one of: {', '.join(PROVIDERS)}."
        )

    # The provider validates the language (code or name) itself.
    try:
        return PROVIDERS[provider](source=source_language, target=target_language)
    except LanguageNotSupportedException:
        raise TranslatorError(
            f"The language '{target_language}' is not supported by {provider} translator."
        ) from None

def translate_text(text, translator):
    try:
        return translator.translate(text)
    except Exception as e:
        raise TranslatorError(str(e)) from e

def split_text(text, max_chars):
    """Split text on line boundaries into chunks shorter than max_chars."""
    limit = max_chars - 1
    chunks = []
    current = None
    for line in text.split("\n"):
        # A single over-long line is hard-split; joining those pieces back
        # with "\n" is the best that can be done.
        while len(line) > limit:
            if current is not None:
                chunks.append(current)
                current = None
            chunks.append(line[:limit])
            line = line[limit:]
        if current is None:
            current = line
        elif len(current) + 1 + len(line) > limit:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}"
    chunks.append(current)
    return chunks

def detect_language(text, provider):
    # deep-translator offers no keyless language detection for these providers.
    raise TranslatorError(f"Language detection is not supported by the {provider} provider.")

def translate_file(file_path, translator, max_chars=MAX_CHARS["Google"]):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except (OSError, UnicodeDecodeError) as e:
        raise TranslatorError(str(e)) from e
    translated_content = "\n".join(
        translate_text(chunk, translator) if chunk.strip() else chunk
        for chunk in split_text(content, max_chars)
    )
    new_file_path = os.path.join(os.path.dirname(file_path), f"translated-{os.path.basename(file_path)}")
    try:
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)
    except OSError as e:
        raise TranslatorError(str(e)) from e
    return new_file_path

def run(args):
    config = load_config()

    if args.source:
        if args.source not in PROVIDERS:
            raise TranslatorError(
                f"Provider '{args.source}' is not supported. Choose one of: {', '.join(PROVIDERS)}."
            )
        config['provider'] = args.source
        save_config(config)
        print(f"Translation provider set to {args.source} permanently.")

    provider = config.get('provider', 'Google')

    if args.detect_language:
        if not args.input:
            raise TranslatorError("Please provide text for language detection.")
        print(f"Detected language: {detect_language(args.input, provider)}")
        return

    if args.input and os.path.isfile(args.input) and args.input.endswith('.txt'):
        if not args.language:
            raise TranslatorError("Please provide a target language with --language")
        translator = get_translator(provider, target_language=args.language)
        result = translate_file(args.input, translator, MAX_CHARS.get(provider, MAX_CHARS["Google"]))
        print(f"Translated file saved to: {result}")
    elif args.input and args.language:
        translator = get_translator(provider, target_language=args.language)
        print(f"Translation: {translate_text(args.input, translator)}")
    elif not args.source:
        raise TranslatorError("Please provide a valid input or option: --language, --detect-language, or --source")

def main(argv=None):
    parser = argparse.ArgumentParser(description='Translation Tool CLI')
    parser.add_argument('input', nargs='?', help='Text or file to translate')
    parser.add_argument('--language', '-l', help='Target language')
    parser.add_argument('--detect-language', '-d', action='store_true', help='Detect the language of the text')
    parser.add_argument('--source', '--provider', help='Set and permanently change translation provider')

    args = parser.parse_args(argv)

    try:
        run(args)
    except TranslatorError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
