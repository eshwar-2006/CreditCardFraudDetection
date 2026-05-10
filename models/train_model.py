import argparse
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import joblib

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(ROOT_DIR, 'dataset', 'creditcard.csv')
MODEL_PATH = os.path.join(ROOT_DIR, 'models', 'model.pkl')
FEATURE_COLUMNS = [
    'Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
    'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
    'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount'
]


def load_data(path=DATA_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f'Dataset not found at {path}')
    return pd.read_csv(path)


def train(data_path=DATA_PATH, model_path=MODEL_PATH):
    df = load_data(data_path)
    if 'Class' not in df.columns:
        raise ValueError("The dataset must contain a 'Class' column.")

    X = df.drop(columns=['Class'])
    y = df['Class']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    pipeline = Pipeline([
        ('model', RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_score = pipeline.predict_proba(X_test)[:, 1]

    print('Training complete')
    print(classification_report(y_test, y_pred))
    print(f'ROC AUC: {roc_auc_score(y_test, y_score):.4f}')

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f'Model saved to {model_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train fraud detection model.')
    parser.add_argument('--data', default=DATA_PATH, help='Path to creditcard.csv')
    parser.add_argument('--output', default=MODEL_PATH, help='Path to save the trained pipeline')
    args = parser.parse_args()
    train(data_path=args.data, model_path=args.output)
