from GrammarEnhancer import GrammarEnhancer
import re
import random

# ==================== Advanced Grammar Checker ====================
class AdvancedGrammarChecker:
    def __init__(self):
        self.encouragements = ["Excellent! 🌟", "Perfect! ✨", "Well done! 👍", "Great job! 🎉"]
        self.grammar_enhancer = GrammarEnhancer()
    
    def _apply_basic_grammar_fixes(self, text):
        corrected = text
        rules = [(r'\bI\s+likes\b', 'I like'), (r'\bI\s+doesn\'t\b', 'I don\'t'),
            (r'\b(she|he|it)\s+don\'t\b', r'\1 doesn\'t'), (r'\b(she|he|it)\s+like\b', r'\1 likes'),
            (r'\b(she|he|it)\s+go\b', r'\1 goes'), (r'\b(have|has)\s+do\b', r'\1 done'),
            (r'\b(have|has)\s+went\b', r'\1 gone'), (r'\bwill\s+played\b', 'will play'),
            (r'\bwill\s+went\b', 'will go'), (r'\bI\s+were\b', 'I was')]
        for pattern, replacement in rules:
            if re.search(pattern, corrected, re.IGNORECASE):
                corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        return corrected
    
    def _apply_formatting_fixes(self, text):
        corrected = re.sub(r'\bi\b', 'I', text)
        sentences = re.split(r'([.!?] +)', corrected)
        for i in range(0, len(sentences), 2):
            if sentences[i] and sentences[i][0].islower():
                sentences[i] = sentences[i][0].upper() + sentences[i][1:]
        corrected = ''.join(sentences)
        if corrected and len(corrected.split()) > 2 and corrected[-1] not in '.!?':
            corrected += '.'
        return corrected
    
    def check_and_correct(self, text):
        if not text or not text.strip():
            return text, "✏️ Write something to get AI feedback..."
        
        corrections = []
        corrected = self._apply_basic_grammar_fixes(text)
        corrected = self._apply_formatting_fixes(corrected)
        
        if corrected == text:
            return corrected, f"🎉 {random.choice(self.encouragements)}"
        else:
            return corrected, f"✨ Suggested correction: \"{corrected}\""
