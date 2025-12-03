import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.preprocessing import LabelEncoder
from src.config import FIG_PATH

def create_visualizations(df):
    print("\nШаг 4: Визуализация данных")
    
    if not os.path.exists(FIG_PATH):
        os.makedirs(FIG_PATH)
    
    sns.set_style("whitegrid")
    
    # Гистограмма возраста
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='age', kde=True, bins=20, color='skyblue')
    plt.title('Распределение возраста клиентов')
    plt.savefig(os.path.join(FIG_PATH, "1_age_distribution.png"))
    plt.close()
    
    # Boxplot (Сумма vs Риск)
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='credit_risk', y='amount', palette="Set2")
    plt.title('Сумма кредита: Хорошие vs Плохие заемщики')
    plt.savefig(os.path.join(FIG_PATH, "2_amount_boxplot.png"))
    plt.close()
    
    # Countplot целей
    plt.figure(figsize=(12, 6))
    order = df['purpose'].value_counts().index
    sns.countplot(data=df, y='purpose', order=order, palette="viridis")
    plt.title('Цели кредитования')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_PATH, "3_purpose_counts.png"))
    plt.close()
    
    # Heatmap
    df_encoded = df.copy()
    le = LabelEncoder()
    for col in df_encoded.select_dtypes(include='object').columns:
        df_encoded[col] = le.fit_transform(df_encoded[col])
        
    plt.figure(figsize=(10, 8))
    cols = ['duration', 'amount', 'age', 'installment_rate', 'number_credits', 'credit_risk']
    sns.heatmap(df_encoded[cols].corr(), annot=True, fmt=".2f", cmap='coolwarm')
    plt.title('Корреляция признаков')
    plt.savefig(os.path.join(FIG_PATH, "4_correlation.png"))
    plt.close()
    
    print(f"Графики сохранены в: {FIG_PATH}")