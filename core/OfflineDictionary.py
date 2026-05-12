# core/OfflineDictionary.py
import json
import gzip
import os

class OfflineDictionary:
    def __init__(self, json_path=None):
        if json_path is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            self.json_path = os.path.join(base_dir, "assets", "full_wordnet.json.gz")
        else:
            self.json_path = json_path
        self.dictionary = self._load_dictionary()
        print(f"✅ Loaded {len(self.dictionary)} words from full JSON dictionary")

    def _load_dictionary(self):
        if os.path.exists(self.json_path):
            try:
                with gzip.open(self.json_path, 'rt', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading JSON: {e}")
                return {}
        return {}

    def get_meaning_with_pronunciation(self, word):
        word_lower = word.lower().strip()
        if word_lower in self.dictionary:
            meanings = self.dictionary[word_lower]
            result = f"📖 **{word.capitalize()}**\n\n"
            for i, meaning in enumerate(meanings[:3], 1):
                result += f"{i}. {meaning['definition']}\n"
                if meaning.get('examples') and meaning['examples']:
                    result += f"   📝 Example: {meaning['examples'][0]}\n"
                result += "\n"
            return result
        else:
            return f"❌ '{word}' not found in dictionary.\n💡 You can add your own meaning manually."
