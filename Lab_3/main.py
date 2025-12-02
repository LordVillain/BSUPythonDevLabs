import sys
import os

from src.config import DATA_PATH
from src.processing import load_data, preprocess_data, get_statistics
from src.visualization import create_visualizations
from src.database import export_to_sql, run_queries

def main():
    print("Запуск программы\n")
    
    # Загрузка и обработка
    df_raw = load_data(DATA_PATH)
    df_clean = preprocess_data(df_raw)
    
    # Аналитика
    get_statistics(df_clean)
    
    # Графики
    create_visualizations(df_clean)
    
    # База данных
    conn = export_to_sql(df_clean)
    run_queries(conn)
    
    print("\nРабота завершена...")

if __name__ == "__main__":
    main()