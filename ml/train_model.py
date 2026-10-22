from pathlib import Path
import re
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ==============================
# PATH
# ==============================

root = Path(__file__).resolve().parents[1]
data = root / 'data'
models = root / 'models'
models.mkdir(exist_ok=True)

norm = lambda x: re.sub(
    r'[^a-z0-9]',
    '',
    str(x).lower()
)


# ==============================
# COLUMN ALIAS
# ==============================

alias = {
    'age': ['age'],
    'gender': ['gender', 'sex'],
    'chestpain': ['chestpain', 'chestpaintype', 'cp'],
    'restingbp': ['restingbp', 'restingbloodpressure', 'trestbps'],
    'cholesterol': [
        'serumcholestrol',
        'serumcholesterol',
        'cholesterol',
        'chol'
    ],
    'fastingbs': ['fastingbloodsugar', 'fastingbs', 'fbs'],
    'restingecg': [
        'restingrelectrocardiogram',
        'restingecg',
        'restecg'
    ],
    'maxheartrate': [
        'maxheartrate',
        'maximumheartrate',
        'thalach'
    ],
    'exerciseangina': [
        'exerciseangia',
        'exerciseangina',
        'exang'
    ],
    'oldpeak': ['oldpeak'],
    'slope': ['slope'],
    'majorvessels': [
        'noofmajorvessels',
        'majorvessels',
        'ca'
    ],
    'target': [
        'target',
        'heartdisease',
        'cardiovasculardisease',
        'output',
        'num'
    ]
}



# LOAD DATASET


files = list(data.rglob('*.csv'))

if not files:
    raise SystemExit(
        'Run python ml/download_dataset.py first'
    )

df = pd.read_csv(files[0])

lookup = {
    norm(c): c
    for c in df.columns
}

m = {
    k: next(
        (
            lookup[norm(a)]
            for a in v
            if norm(a) in lookup
        ),
        None
    )
    for k, v in alias.items()
}

if not m['target']:
    raise SystemExit(
        f'Target not found. Columns: {list(df.columns)}'
    )


# ==============================
# FEATURES
# ==============================

keys = [
    k
    for k in alias
    if k != 'target' and m[k]
]

X = df[
    [m[k] for k in keys]
].copy()

X.columns = keys


# ==============================
# TARGET
# ==============================

y = (
    pd.to_numeric(
        df[m['target']],
        errors='coerce'
    )
    .fillna(0) > 0
).astype(int)


# ==============================
# COLUMNS
# ==============================

cat = [
    k for k in keys
    if k in [
        'gender',
        'chestpain',
        'fastingbs',
        'restingecg',
        'exerciseangina',
        'slope',
        'majorvessels'
    ]
]

num = [
    k for k in keys
    if k not in cat
]

for c in num:
    X[c] = pd.to_numeric(
        X[c],
        errors='coerce'
    )


# ==============================
# TRAIN TEST SPLIT
# ==============================

xt, xv, yt, yv = train_test_split(
    X,
    y,
    test_size=.2,
    random_state=42,
    stratify=y
)


# ==============================
# PREPROCESSING
# ==============================

pre = ColumnTransformer([

    (
        'num',
        Pipeline([
            (
                'imputer',
                SimpleImputer(strategy='median')
            ),
            (
                'scale',
                StandardScaler()
            )
        ]),
        num
    ),

    (
        'cat',
        Pipeline([
            (
                'imputer',
                SimpleImputer(
                    strategy='most_frequent'
                )
            ),
            (
                'oh',
                OneHotEncoder(
                    handle_unknown='ignore'
                )
            )
        ]),
        cat
    )
])


# ==============================
# MODELS
# ==============================

model_list = [

    (
        'Logistic Regression',
        LogisticRegression(
            max_iter=2000,
            class_weight='balanced'
        )
    ),

    (
        'Random Forest',
        RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight='balanced'
        )
    )
]


results = {}

best = None
bestrec = -1
bestname = ''


# ==============================
# TRAINING
# ==============================

for name, clf in model_list:

    model = Pipeline([
        ('pre', pre),
        ('model', clf)
    ])

    model.fit(xt, yt)

    pred = model.predict(xv)

    acc = accuracy_score(yv, pred)
    
    precision = precision_score(yv, pred, zero_division=0)
    
    recall = recall_score( yv, pred, zero_division=0)
    
    f1 = f1_score( yv, pred,zero_division=0)

    cm = confusion_matrix( yv,pred)

    print("\n==============================")
    print(name)
    print("==============================")

    print( f"Accuracy : {acc * 100:.2f}%")

    print(f"Precision: {precision * 100:.2f}%")

    print( f"Recall   : {recall * 100:.2f}%")

    print( f"F1 Score : {f1 * 100:.2f}%")

    print("Confusion Matrix:\n", cm)

    results[name] = {

        'accuracy': acc * 100,

        'precision': precision * 100,

        'recall': recall * 100,

        'f1': f1 * 100,

        'confusion_matrix': cm,

        'model': model,

        'y_test': yv.to_numpy(),

        'y_pred': pred,

        'X_test': xv
    }

    # Best model based on Recall

    if recall > bestrec:

        best = model
        bestrec = recall
        bestname = name


# ==============================
# SAVE BEST MODEL
# ==============================

joblib.dump(
    {
        'model': best,
        'features': keys,
        'model_name': bestname,
        'test_recall': bestrec
    },
    models / 'heart_india_model.joblib'
)


# ==============================
# SAVE RESULTS FOR GRAPHS
# ==============================

joblib.dump( results, models / 'model_results.joblib')


print("\n================================")
print("FINAL RESULT")
print("================================")

print( f"Best Model : {bestname}")

print( f"Best Recall: {bestrec * 100:.2f}%")

print("Model Saved:", models / 'heart_india_model.joblib')

print("Results Saved:", models / 'model_results.joblib')

print("================================")