import pandas as pd
from src.config import COLUMN_NAMES, DECODE_MAP

def load_data(path):
    print("Шаг 1: Загрузка данных")
    try:
        df = pd.read_csv(path, sep=' ', names=COLUMN_NAMES)
        print(f"Данные успешно загружены. Размер: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"ОШИБКА: Файл не найден по пути {path}")
        raise

def preprocess_data(df):
    print("\nШаг 2: Предобработка данных")
    
    missing = df.isnull().sum().sum()
    print(f"Пропущенных значений: {missing}")
    
    # Декодирование
    df_readable = df.copy()
    for col, mapping in DECODE_MAP.items():
        if col in df_readable.columns:
            df_readable[col] = df_readable[col].map(mapping).fillna(df_readable[col])
            
    # Целевая переменная
    df_readable['credit_risk'] = df_readable['credit_risk'].map({1: 'Good', 2: 'Bad'})
    
    print("Данные расшифрованы и подготовлены.")
    return df_readable

def get_statistics(df):
    print("\nШаг 3: Статистика")
    print("Средние значения:")
    print(df[['age', 'amount', 'duration']].describe().round(2))
    print("\nБаланс классов:")
    print(df['credit_risk'].value_counts(normalize=True).round(2))