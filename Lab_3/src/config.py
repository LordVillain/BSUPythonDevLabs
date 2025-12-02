import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'german.data')
DB_PATH = os.path.join(BASE_DIR, 'output', 'database', 'credit_data.db')
FIG_PATH = os.path.join(BASE_DIR, 'output', 'figures')

COLUMN_NAMES = [
    'status', 'duration', 'credit_history', 'purpose', 'amount',
    'savings', 'employment_duration', 'installment_rate', 'personal_status_sex',
    'other_debtors', 'present_residence', 'property', 'age',
    'other_installment_plans', 'housing', 'number_credits', 'job',
    'people_liable', 'telephone', 'foreign_worker', 'credit_risk'
]

DECODE_MAP = {
    'status': {
        'A11': '< 0 DM', 'A12': '0 <= ... < 200 DM', 'A13': '>= 200 DM / Salary', 'A14': 'no checking account'
    },
    'credit_history': {
        'A30': 'no credits taken', 'A31': 'all credits paid back', 'A32': 'existing credits paid back',
        'A33': 'delay in paying in past', 'A34': 'critical account'
    },
    'purpose': {
        'A40': 'car (new)', 'A41': 'car (used)', 'A42': 'furniture/equipment',
        'A43': 'radio/television', 'A44': 'domestic appliances', 'A45': 'repairs',
        'A46': 'education', 'A47': 'vacation', 'A48': 'retraining',
        'A49': 'business', 'A410': 'others'
    },
    'savings': {
        'A61': '< 100 DM', 'A62': '100 <= ... < 500 DM', 'A63': '500 <= ... < 1000 DM',
        'A64': '>= 1000 DM', 'A65': 'unknown/no savings'
    },
    'employment_duration': {
        'A71': 'unemployed', 'A72': '< 1 year', 'A73': '1 <= ... < 4 years',
        'A74': '4 <= ... < 7 years', 'A75': '>= 7 years'
    },
    'personal_status_sex': {
        'A91': 'male: divorced/separated', 'A92': 'female: divorced/separated/married',
        'A93': 'male: single', 'A94': 'male: married/widowed', 'A95': 'female: single'
    },
    'housing': {
        'A151': 'rent', 'A152': 'own', 'A153': 'for free'
    },
    'job': {
        'A171': 'unemployed/unskilled', 'A172': 'unskilled - resident',
        'A173': 'skilled employee', 'A174': 'management/self-employed'
    }
}