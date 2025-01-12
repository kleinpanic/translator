import argparse
import os
from deep_translator import GoogleTranslator, MyMemoryTranslator, PonsTranslator
import json

# Configuration file path
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {"provider": "Google"}  # Default provider

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

def get_translator(provider, source_language='auto', target_language='en'):
    providers = {
        "Google": GoogleTranslator,
        "MyMemory": MyMemoryTranslator,
        "Pons": PonsTranslator
    }
    if provider not in providers:
        raise ValueError(f"Provider '{provider}' is not supported.")
    
    # Ensure the target language is supported by the selected provider
    translator = providers[provider](source=source_language, target=target_language)
    if target_language not in translator.get_supported_languages(as_dict=True).values():
        raise ValueError(f"The language '{target_language}' is not supported by {provider} translator.")
    
    return translator

def translate_text(text, translator):
    try:
        return translator.translate(text)
    except Exception as e:
        return f"Error: {str(e)}"

def detect_language(text, provider):
    try:
        if provider == "MyMemory":
            return MyMemoryTranslator().detect(text)
        else:
            return "Error: Language detection is not supported by the selected provider."
    except Exception as e:
        return f"Error: {str(e)}"

def translate_file(file_path, translator):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        translated_content = translate_text(content, translator)
        new_file_path = os.path.join(os.path.dirname(file_path), f"translated-{os.path.basename(file_path)}")
        with open(new_file_path, 'w') as file:
            file.write(translated_content)
        return new_file_path
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    config = load_config()
    parser = argparse.ArgumentParser(description='Translation Tool CLI')
    parser.add_argument('input', nargs='?', help='Text or file to translate')
    parser.add_argument('--language', '-l', help='Target language')
    parser.add_argument('--detect-language', '-d', action='store_true', help='Detect the language of the text')
    parser.add_argument('--source', '--provider', help='Set and permanently change translation provider')

    args = parser.parse_args()

    if args.source:
        config['provider'] = args.source
        save_config(config)
        print(f"Translation provider set to {args.source} permanently.")
    
    translator = get_translator(config['provider'], target_language=args.language or 'en')

    if args.detect_language:
        if args.input:
            result = detect_language(args.input, config['provider'])
            print(f"Detected language: {result}")
        else:
            print("Please provide text for language detection.")
        return

    if args.input and os.path.isfile(args.input) and args.input.endswith('.txt'):
        if args.language:
            result = translate_file(args.input, translator)
            print(f"Translated file saved to: {result}")
        else:
            print("Please provide a target language with --language")
    elif args.input and args.language:
        result = translate_text(args.input, translator)
        print(f"Translation: {result}")
    else:
        print("Please provide a valid input or option: --language, --detect-language, or --source")

if __name__ == '__main__':
    main()

