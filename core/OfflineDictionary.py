import re
from nltk.corpus import wordnet as wn
import pronouncing

# ==================== Offline Dictionary ====================
class OfflineDictionary:
    def __init__(self):
        self.custom_pronounce = {'the': 'ðə', 'a': 'ə', 'an': 'ən', 'and': 'ænd', 'of': 'ʌv',
            'to': 'tuː', 'in': 'ɪn', 'for': 'fɔr', 'with': 'wɪð', 'on': 'ɑn'}
        self.arpabet_to_ipa = {'AA': 'ɑ', 'AE': 'æ', 'AH': 'ə', 'AO': 'ɔ', 'AW': 'aʊ', 'AY': 'aɪ',
            'EH': 'ɛ', 'ER': 'ɜr', 'EY': 'eɪ', 'IH': 'ɪ', 'IY': 'i', 'OW': 'oʊ', 'OY': 'ɔɪ',
            'UH': 'ʊ', 'UW': 'u', 'B': 'b', 'D': 'd', 'DH': 'ð', 'F': 'f', 'G': 'g', 'HH': 'h',
            'JH': 'dʒ', 'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'P': 'p', 'R': 'r',
            'S': 's', 'SH': 'ʃ', 'T': 't', 'TH': 'θ', 'V': 'v', 'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'}
    
    def convert_arpabet_to_readable(self, arpabet):
        if not arpabet: return ""
        parts = arpabet.split()
        readable = []
        for part in parts:
            base_part = re.sub(r'[0-9]', '', part)
            readable.append(self.arpabet_to_ipa.get(base_part, base_part.lower()))
        return ''.join(readable)
    
    def get_pronunciation_text(self, word):
        word_lower = word.lower().strip()
        if word_lower in self.custom_pronounce:
            return f"/{self.custom_pronounce[word_lower]}/"
        phones = pronouncing.phones_for_word(word_lower)
        if phones:
            return f"/{self.convert_arpabet_to_readable(phones[0])}/"
        return None
    
    def get_meaning_with_pronunciation(self, word):
        word_lower = word.lower().strip()
        synsets = wn.synsets(word_lower)
        if not synsets:
            return f"❌ '{word}' not found in dictionary.\n💡 You can add your own meaning manually."
        result = f"📖 {word.capitalize()}\n\n"
        pron = self.get_pronunciation_text(word)
        if pron: result += f"🔊 Pronunciation: {pron}\n\n"
        for i, syn in enumerate(synsets[:3], 1):
            result += f"{i}. {syn.definition()}\n"
            if syn.examples(): result += f"   📝 {syn.examples()[0]}\n"
            result += "\n"
        return result.strip()
