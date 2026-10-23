import re

from .models import HeavyWord, ValidationRule


def validate_text(text):
    """
    Проверяет текст на когнитивную сложность.
    Возвращает словарь с результатами.
    """
    if not text:
        return {"score": 0.0, "is_passed": True, "details": {}}

    # 1. Ищем тяжелые слова
    found_words = []
    total_weight = 0
    words_in_text = re.findall(r'\b\w+\b', text.lower())
    
    heavy_words_db = HeavyWord.objects.all()
    heavy_dict = {hw.word.lower(): hw for hw in heavy_words_db}

    for word in words_in_text:
        if word in heavy_dict:
            hw = heavy_dict[word]
            found_words.append({
                "word": hw.word,
                "suggestion": hw.suggestion,
                "category": hw.category,
            })
            total_weight += hw.weight

    # 2. Проверяем длину предложений
    long_sentences = []
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        word_count = len(re.findall(r'\b\w+\b', sentence))
        if word_count > 20:  # Порог из нашего правила
            long_sentences.append({
                "text": sentence,
                "word_count": word_count,
            })

    # 3. Считаем общий балл (чем больше — тем хуже)
    # Нормируем вес слов и длину предложений
    words_score = min(total_weight / 10.0, 1.0)
    sentences_score = min(len(long_sentences) / 3.0, 1.0)
    
    final_score = round(0.6 * words_score + 0.4 * sentences_score, 2)

    return {
        "score": final_score,
        "is_passed": final_score < 0.5,  # Если меньше 0.5 — текст хороший
        "details": {
            "heavy_words": found_words,
            "long_sentences": long_sentences,
        }
    }
