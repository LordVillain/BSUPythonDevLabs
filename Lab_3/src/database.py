import sqlite3
import pandas as pd
import os
from src.config import DB_PATH

def export_to_sql(df):
    print("\nШаг 5: База данных")
    
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
        
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('clients', conn, if_exists='replace', index=False)
    print("Таблица 'clients' успешно обновлена/создана")
    return conn

def run_queries(conn):    
    queries = [
        (
            "1. ВЫБОРКА: Топ-3 самых молодых надежных заемщиков", 
            """
            SELECT age, purpose, amount, housing
            FROM clients 
            WHERE credit_risk = 'Good' 
            ORDER BY age ASC 
            LIMIT 3
            """
        ),
        (
            "2. АГРЕГАЦИЯ: Средний кредит по целям (Топ-5 самых дорогих категорий)", 
            """
            SELECT purpose, ROUND(AVG(amount), 0) as avg_loan_dm, COUNT(*) as deals_count
            FROM clients 
            GROUP BY purpose 
            ORDER BY avg_loan_dm DESC 
            LIMIT 5
            """
        ),
        (
            "3. ГРУППИРОВКА: Портрет заемщика (Сравнение Good vs Bad)",
            """
            SELECT credit_risk, 
                   ROUND(AVG(age), 1) as avg_age, 
                   ROUND(AVG(amount), 0) as avg_amount,
                   ROUND(AVG(duration), 1) as avg_duration_months
            FROM clients
            GROUP BY credit_risk
            """
        ),
        (
            "4. АНАЛИЗ РИСКОВ: Влияние типа жилья на риск (Crosstab)",
            """
            SELECT housing, credit_risk, COUNT(*) as client_count
            FROM clients
            GROUP BY housing, credit_risk
            ORDER BY housing, credit_risk
            """
        ),
        (
            "5. ФИЛЬТР: Клиенты с 'Критическим счетом', взявшие более 5000 DM",
            """
            SELECT job, amount, age, purpose
            FROM clients
            WHERE credit_history = 'critical account' AND amount > 5000
            ORDER BY amount DESC
            LIMIT 5
            """
        )
    ]
    
    for title, sql in queries:
        print(f"\n[SQL] {title}")
        print(pd.read_sql(sql, conn))
        print("-" * 50)
        
    conn.close()