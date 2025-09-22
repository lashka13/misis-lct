#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для извлечения только текстов отзывов из JSON файла
"""

import json
import pandas as pd

def extract_reviews_text(json_file_path):
    """
    Извлекает только тексты отзывов из JSON файла
    
    Args:
        json_file_path (str): Путь к JSON файлу
        
    Returns:
        list: Список текстов отзывов
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            reviews = json.load(file)
        
        # Извлекаем только тексты отзывов
        review_texts = []
        for review in reviews:
            if isinstance(review, dict) and 'review' in review:
                review_texts.append(review['review'])
        
        print(f"✅ Извлечено {len(review_texts)} текстов отзывов")
        return review_texts
        
    except FileNotFoundError:
        print(f"❌ Файл {json_file_path} не найден")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка при парсинге JSON: {e}")
        return []
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return []

def create_simple_dataset(review_texts):
    """
    Создает простой датасет только с текстами отзывов
    
    Args:
        review_texts (list): Список текстов отзывов
        
    Returns:
        pd.DataFrame: Датасет с текстами отзывов
    """
    if not review_texts:
        print("❌ Нет текстов для обработки")
        return pd.DataFrame()
    
    # Создаем DataFrame только с текстами
    df = pd.DataFrame({
        'review_text': review_texts
    })
    
    print(f"✅ Создан датасет с {len(df)} отзывами")
    return df

def main():
    """
    Основная функция
    """
    # Путь к JSON файлу
    json_file = "/Users/nikitamesh/LCT/sravni.json"
    
    print("🚀 Извлекаем тексты отзывов из JSON файла...")
    
    # Извлекаем тексты отзывов
    review_texts = extract_reviews_text(json_file)
    
    if not review_texts:
        print("❌ Не удалось извлечь тексты отзывов")
        return
    
    # Создаем датасет
    df = create_simple_dataset(review_texts)
    
    if df.empty:
        print("❌ Не удалось создать датасет")
        return
    
    # Сохраняем в CSV
    output_file = "/Users/nikitamesh/LCT/reviews_text_only.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"✅ Датасет сохранен в файл: {output_file}")
    print(f"📊 Количество отзывов: {len(df)}")
    print(f"📝 Пример первого отзыва:")
    print(f"   \"{df['review_text'].iloc[0][:100]}...\"")

if __name__ == "__main__":
    main()
