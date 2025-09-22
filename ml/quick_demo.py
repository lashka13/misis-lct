#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая демонстрация кластеризации на небольшой выборке отзывов
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer
import warnings
warnings.filterwarnings('ignore')

def quick_demo_clustering(csv_file, sample_size=500, n_clusters=5):
    """
    Быстрая демонстрация кластеризации на выборке отзывов
    
    Args:
        csv_file (str): Путь к CSV файлу с отзывами
        sample_size (int): Размер выборки для демонстрации
        n_clusters (int): Количество кластеров
    """
    print("🚀 Быстрая демонстрация кластеризации...")
    
    print("📖 Загружаем отзывы...")
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    if len(df) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
        print(f"✅ Взята выборка из {sample_size} отзывов из {len(df)}")
    else:
        df_sample = df
        print(f"✅ Используем все {len(df)} отзывов")
    
    # Загружаем модель
    print("🔄 Загружаем модель...")
    model = SentenceTransformer('cointegrated/rubert-tiny2')
    
    # Создаем эмбеддинги
    print("🔄 Создаем эмбеддинги...")
    texts = df_sample['review_text'].fillna('').astype(str).tolist()
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    print(f"✅ Создано {len(embeddings)} эмбеддингов")
    
    # Кластеризация
    print("🔄 Кластеризуем отзывы...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(embeddings)
    
    # Добавляем метки кластеров
    df_sample = df_sample.copy()
    df_sample['cluster'] = cluster_labels
    
    # Анализируем кластеры
    print("📊 Анализируем кластеры...")
    cluster_analysis = []
    
    for cluster_id in range(n_clusters):
        cluster_reviews = df_sample[df_sample['cluster'] == cluster_id]
        
        cluster_info = {
            'cluster_id': cluster_id,
            'size': len(cluster_reviews),
            'percentage': len(cluster_reviews) / len(df_sample) * 100,
            'avg_length': cluster_reviews['review_text'].str.len().mean(),
            'sample_reviews': cluster_reviews['review_text'].head(3).tolist()
        }
        cluster_analysis.append(cluster_info)
    
    # Выводим результаты
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТЫ КЛАСТЕРИЗАЦИИ")
    print("="*60)
    
    for info in sorted(cluster_analysis, key=lambda x: x['size'], reverse=True):
        print(f"\n🔹 Кластер {info['cluster_id']} ({info['size']} отзывов, {info['percentage']:.1f}%)")
        print(f"   Средняя длина: {info['avg_length']:.0f} символов")
        print("   Примеры отзывов:")
        for i, sample in enumerate(info['sample_reviews'], 1):
            print(f"     {i}. {sample[:100]}{'...' if len(sample) > 100 else ''}")
    
    # Визуализация
    print("\n🔄 Создаем визуализацию...")
    pca = PCA(n_components=2, random_state=42)
    reduced_embeddings = pca.fit_transform(embeddings)
    
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], 
                        c=cluster_labels, cmap='tab10', alpha=0.7, s=30)
    plt.colorbar(scatter)
    plt.title('Кластеризация отзывов по темам (демо)', fontsize=16)
    plt.xlabel('Первая главная компонента', fontsize=12)
    plt.ylabel('Вторая главная компонента', fontsize=12)
    
    # Добавляем подписи кластеров
    for i in range(n_clusters):
        cluster_center = reduced_embeddings[cluster_labels == i].mean(axis=0)
        plt.annotate(f'Кластер {i}', cluster_center, fontsize=12, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.savefig('/Users/nikitamesh/LCT/demo_clusters.png', dpi=200, bbox_inches='tight')
    plt.show()
    
    # Сохраняем результаты
    print("💾 Сохраняем результаты...")
    df_sample.to_csv('/Users/nikitamesh/LCT/demo_clustered_reviews.csv', index=False, encoding='utf-8')
    
    analysis_df = pd.DataFrame(cluster_analysis)
    analysis_df.to_csv('/Users/nikitamesh/LCT/demo_cluster_analysis.csv', index=False, encoding='utf-8')
    
    print("✅ Результаты сохранены:")
    print("   - demo_clustered_reviews.csv - отзывы с кластерами")
    print("   - demo_cluster_analysis.csv - анализ кластеров")
    print("   - demo_clusters.png - визуализация")
    
    return df_sample, analysis_df

if __name__ == "__main__":
    df, analysis = quick_demo_clustering('/Users/nikitamesh/LCT/reviews_text_only.csv', 
                                       sample_size=300, n_clusters=5)
