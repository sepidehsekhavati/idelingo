import json
import os
from datetime import datetime

# مسیر فایل JSON
GRAMMAR_JSON_PATH = os.path.join(os.path.dirname(__file__), "../assets/grammar_rules.json")

# ==================== Grammar Enhancer ====================
class GrammarEnhancer:
    def __init__(self, json_file=GRAMMAR_JSON_PATH):
        self.json_file = json_file
        self.favorites_file = json_file.replace('.json', '_favorites.json')
        self.notes_file = json_file.replace('.json', '_notes.json')
        self.rules = self._load_rules()
        self.favorites = self._load_favorites()
        self.notes = self._load_notes()
        print(f"✅ Loaded {len(self.rules)} grammar rules")
    
    def _get_default_rules(self):
        return {
            "simple present": {
                "title": "Simple Present Tense",
                "structure": "Subject + base verb (add -s/-es for third person singular)",
                "example": ["I work every day.", "She works at a bank.", "They play football."],
                "usage": ["Habits and routines", "General facts"],
                "common_mistakes": ["❌ He go to school → ✅ He goes to school"],
                "formula": "S + V1(s/es) + O", "level": "beginner", "keywords": ["always", "usually", "often"]
            },
            "present continuous": {
                "title": "Present Continuous Tense", "level": "beginner",
                "structure": "Subject + am/is/are + verb-ing",
                "example": ["I am reading a book now.", "She is cooking dinner."],
                "usage": ["Actions happening right now", "Temporary situations"],
                "common_mistakes": ["❌ I am knowing → ✅ I know"],
                "formula": "S + am/is/are + V-ing + O", "keywords": ["now", "right now", "at the moment"]
            },
            "simple past": {
                "title": "Simple Past Tense", "level": "beginner",
                "structure": "Subject + past verb (regular: -ed, irregular forms)",
                "example": ["I visited Paris last year.", "She bought a new car."],
                "usage": ["Completed actions in the past", "Past habits"],
                "common_mistakes": ["❌ I go yesterday → ✅ I went yesterday"],
                "formula": "S + V2 + O", "keywords": ["yesterday", "last week", "ago"]
            },
            "present perfect": {
                "title": "Present Perfect Tense", "level": "intermediate",
                "structure": "Subject + have/has + past participle",
                "example": ["I have finished my homework.", "She has visited Japan."],
                "usage": ["Past actions with present results", "Life experiences"],
                "common_mistakes": ["❌ I have went → ✅ I have gone"],
                "formula": "S + have/has + V3 + O", "keywords": ["ever", "never", "already", "yet", "since", "for"]
            },
            "first conditional": {
                "title": "First Conditional", "level": "intermediate",
                "structure": "If + present simple, will + base verb",
                "example": ["If it rains, I will stay home.", "If you study, you will pass."],
                "usage": ["Real/possible future situations"],
                "common_mistakes": ["❌ If I will see → ✅ If I see"],
                "formula": "If + S + V1, S + will + V1", "keywords": ["if", "when", "unless"]
            },
            "second conditional": {
                "title": "Second Conditional", "level": "intermediate",
                "structure": "If + past simple, would + base verb",
                "example": ["If I were rich, I would travel.", "If she knew, she would tell."],
                "usage": ["Imaginary/unreal situations"],
                "common_mistakes": ["❌ If I would be rich → ✅ If I were rich"],
                "formula": "If + S + V2, S + would + V1", "keywords": ["if", "would", "could", "might"]
            },
            "passive voice": {
                "title": "Passive Voice", "level": "intermediate",
                "structure": "Object + be + past participle + (by subject)",
                "example": ["The book is read by many.", "English is spoken here."],
                "usage": ["Focus on action receiver", "Unknown doer"],
                "common_mistakes": ["❌ The book is readed → ✅ The book is read"],
                "formula": "O + am/is/are + V3 + (by S)", "keywords": ["by", "is", "are", "was", "were"]
            }
        }
    
    def _load_rules(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        default_rules = self._get_default_rules()
        self._save_rules(default_rules)
        return default_rules
    
    def _save_rules(self, rules=None):
        if rules is None: rules = self.rules
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(rules, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_favorites(self):
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_notes(self):
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_grammar_info(self, topic):
        topic_lower = topic.lower().strip()
        if topic_lower in self.rules:
            return self.rules[topic_lower]
        for key, value in self.rules.items():
            if topic_lower in key or key in topic_lower:
                return value
        return None
    
    def get_all_topics(self):
        return list(self.rules.keys())
    
    def search_grammar(self, query):
        query_lower = query.lower().strip()
        results = []
        for key, value in self.rules.items():
            if (query_lower in key or query_lower in value.get('title', '').lower() or
                query_lower in value.get('structure', '').lower()):
                results.append((key, value))
        return results
    
    def get_rules_by_level(self, level):
        results = []
        for key, rule in self.rules.items():
            if rule.get('level', '').lower() == level.lower():
                results.append((key, rule))
        return results
    
    def add_favorite(self, topic):
        if not any(fav['key'] == topic for fav in self.favorites):
            rule = self.get_grammar_info(topic)
            if rule:
                self.favorites.append({'key': topic, 'title': rule.get('title', topic),
                                       'added_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                self._save_favorites()
                return True
        return False
    
    def remove_favorite(self, topic):
        for i, fav in enumerate(self.favorites):
            if fav['key'] == topic:
                self.favorites.pop(i)
                self._save_favorites()
                return True
        return False
    
    def get_favorites(self):
        return self.favorites
    
    def is_favorite(self, topic):
        return any(fav['key'] == topic for fav in self.favorites)
    
    def save_note(self, topic, note):
        if topic not in self.notes:
            self.notes[topic] = []
        self.notes[topic].append({'note': note, 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        self._save_notes()
        return True
    
    def get_notes(self, topic):
        return self.notes.get(topic, [])
    
    def get_grammar_stats(self):
        stats = {'total_rules': len(self.rules), 'by_level': {'beginner': 0, 'intermediate': 0, 'advanced': 0},
                 'favorites_count': len(self.favorites)}
        for rule in self.rules.values():
            level = rule.get('level', 'beginner')
            if level in stats['by_level']:
                stats['by_level'][level] += 1
        return stats
    
    def check_sentence_grammar(self, sentence):
        sentence_lower = sentence.lower().strip()
        errors = []
        for rule_key, rule in self.rules.items():
            for mistake in rule.get('common_mistakes', []):
                if '❌' in mistake and '✅' in mistake:
                    wrong = mistake.split('❌')[1].split('→')[0].strip()
                    correct = mistake.split('→')[1].split('✅')[0].strip()
                    if wrong.lower() in sentence_lower:
                        errors.append({'rule': rule.get('title', rule_key), 'error': wrong,
                                       'suggestion': correct, 'explanation': rule.get('structure', '')})
        return errors, []
