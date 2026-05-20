
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# ---------------- LOAD DATA ----------------

conn = sqlite3.connect("finance.db")

df = pd.read_sql_query(
    "SELECT * FROM expenses",
    conn
)

conn.close()

# ---------------- CHECK DATA ----------------

if len(df) < 2:

    print("Add more expenses before training.")

else:

    # ---------------- CREATE FEATURES ----------------

    df['index'] = range(1, len(df)+1)

    X = df[['index']]
    y = df['amount']

    # ---------------- TRAIN MODEL ----------------

    model = LinearRegression()

    model.fit(X, y)

    # ---------------- SAVE MODEL ----------------

    joblib.dump(
        model,
        "expense_prediction_model.pkl"
    )

    print("Model Trained Successfully")
