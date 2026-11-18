import re
from .models import HeavyWord

def validate_and_clean_text(text):
    """Проверяет текст, считает сложность и возвращает очищенную версию."""
    if not text:
        return {"score": 0.0, "is_passed": True, "clean_text": "", "details": {}}

    found_words = []
    total_weight = 0
    
    # Ищем тяжелые слова (независимо от регистра)
    heavy_words_db = HeavyWord.objects.all()
    heavy_dict = {hw.word.lower(): hw for hw in heavy_words_db}
    
    clean_text = text
    
    words_in_text = re.findall(r'\b\w+\b', text.lower())
    for word in set(words_in_text):
        if word in heavy_dict:
            hw = heavy_dict[word]
            found_words.append({"word": hw.word, "suggestion": hw.suggestion})
            total_weight += hw.weight
            
            # АВТОЗАМЕНА: заменяем слово с сохранением регистра первой буквы
            if hw.suggestion:
                # Делаем замену без учета регистра
                pattern = re.compile(re.escape(hw.word), re.IGNORECASE)
                clean_text = pattern.sub(hw.suggestion, clean_text)

    # Проверяем длину предложений
    sentences = re.split(r'[.!?]+', text)
    long_sentences = 0
    for s in sentences:
        if len(re.findall(r'\b\w+\b', s)) > 20:
            long_sentences += 1

    # Считаем балл
    words_score = min(total_weight / 10.0, 1.0)
    final_score = round(words_score, 2)
    
    # Считаем текст плохим, если есть тяжелые слова
    is_passed = (len(found_words) == 0) and (long_sentences == 0)

    return {
        "score": final_score,
        "is_passed": is_passed,
        "clean_text": clean_text, # <--- ВОТ ОН, ОЧИЩЕННЫЙ ТЕКСТ
        "details": {"heavy_words": found_words, "long_sentences": long_sentences}
    }