
import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
import plotly.express as px
import joblib
import numpy as np

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="FinGuide AI",
    page_icon="💰",
    layout="wide"
)

# ---------------- DATABASE ----------------

def create_connection():

    return sqlite3.connect("finance.db")

# ---------------- USER FUNCTIONS ----------------

def register_user(username, password):

    conn = create_connection()

    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    try:

        cursor.execute(
            """
            INSERT INTO users(username, password)
            VALUES (?, ?)
            """,
            (username, hashed_password)
        )

        conn.commit()

        return True

    except:

        return False

    finally:

        conn.close()

def login_user(username, password):

    conn = create_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE username=?
        """,
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        stored_password = user[2]

        if bcrypt.checkpw(
            password.encode('utf-8'),
            stored_password
        ):

            return True

    return False

# ---------------- EXPENSE FUNCTIONS ----------------

def add_expense(category, amount, note):

    conn = create_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO expenses(category, amount, note)
        VALUES (?, ?, ?)
        """,
        (category, amount, note)
    )

    conn.commit()

    conn.close()

def load_expenses():

    conn = create_connection()

    df = pd.read_sql_query(
        "SELECT * FROM expenses",
        conn
    )

    conn.close()

    return df

# ---------------- INCOME FUNCTIONS ----------------

def add_income(source, amount):

    conn = create_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO income(source, amount)
        VALUES (?, ?)
        """,
        (source, amount)
    )

    conn.commit()

    conn.close()

def load_income():

    conn = create_connection()

    df = pd.read_sql_query(
        "SELECT * FROM income",
        conn
    )

    conn.close()

    return df

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

# ---------------- AUTH SCREEN ----------------

if not st.session_state.logged_in:

    st.title("💰 FinGuide AI")

    auth_mode = st.sidebar.selectbox(
        "Authentication",
        ["Login", "Register"]
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    # REGISTER

    if auth_mode == "Register":

        if st.button("Register"):

            success = register_user(
                username,
                password
            )

            if success:

                st.success(
                    "Registration Successful ✅"
                )

            else:

                st.error(
                    "Username already exists"
                )

    # LOGIN

    else:

        if st.button("Login"):

            success = login_user(
                username,
                password
            )

            if success:

                st.session_state.logged_in = True

                st.rerun()

            else:

                st.error(
                    "Invalid Credentials"
                )

# ---------------- MAIN APP ----------------

else:

    st.sidebar.title("💰 FinGuide AI")

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Income Manager",
            "Expense Entry",
            "Analytics",
            "Budget Planner",
            "Predictions",
            "Settings"
        ]
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False

        st.rerun()

    # LOAD DATA

    expense_df = load_expenses()

    income_df = load_income()

    total_income = (
        income_df['amount'].sum()
        if not income_df.empty else 0
    )

    total_expense = (
        expense_df['amount'].sum()
        if not expense_df.empty else 0
    )

    savings = total_income - total_expense

    # ---------------- DASHBOARD ----------------

    if menu == "Dashboard":

        st.title("💰 FinGuide AI Dashboard")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Income",
            f"₹{total_income}"
        )

        col2.metric(
            "Total Expenses",
            f"₹{total_expense}"
        )

        col3.metric(
            "Savings",
            f"₹{savings}"
        )

        st.markdown("---")

        # Financial Health

        if total_income > 0:

            ratio = (
                savings / total_income
            ) * 100

        else:

            ratio = 0

        st.subheader("Financial Health")

        if ratio >= 40:

            st.success("Excellent 🟢")

        elif ratio >= 20:

            st.warning("Good 🟡")

        else:

            st.error("Poor 🔴")

        # Charts

        if not expense_df.empty:

            category_data = expense_df.groupby(
                'category'
            )['amount'].sum().reset_index()

            fig = px.pie(
                category_data,
                names='category',
                values='amount',
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # ---------------- INCOME MANAGER ----------------

    elif menu == "Income Manager":

        st.title("💵 Income Manager")

        source = st.selectbox(
            "Income Source",
            [
                "Salary",
                "Freelancing",
                "Investments",
                "Business",
                "Other"
            ]
        )

        amount = st.number_input(
            "Income Amount",
            min_value=0.0
        )

        if st.button("Add Income"):

            add_income(source, amount)

            st.success(
                "Income Added Successfully ✅"
            )

        st.subheader("Income History")

        st.dataframe(income_df)

    # ---------------- EXPENSE ENTRY ----------------

    elif menu == "Expense Entry":

        st.title("➕ Add Expense")

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Transport",
                "Bills",
                "Entertainment",
                "Healthcare",
                "Education",
                "Shopping"
            ]
        )

        amount = st.number_input(
            "Expense Amount",
            min_value=0.0
        )

        note = st.text_input("Note")

        if st.button("Save Expense"):

            add_expense(
                category,
                amount,
                note
            )

            st.success(
                "Expense Added Successfully ✅"
            )

    # ---------------- ANALYTICS ----------------

    elif menu == "Analytics":

        st.title("📊 Financial Analytics")

        if not expense_df.empty:

            category_data = expense_df.groupby(
                'category'
            )['amount'].sum().reset_index()

            fig = px.bar(
                category_data,
                x='category',
                y='amount',
                text='amount',
                color='category'
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader("Expense History")

            st.dataframe(expense_df)

        else:

            st.info("No expense data available.")

    # ---------------- BUDGET ----------------

    elif menu == "Budget Planner":

        st.title("💵 Budget Planner")

        monthly_budget = st.number_input(
            "Monthly Budget",
            min_value=0.0
        )

        remaining = (
            monthly_budget - total_expense
        )

        st.metric(
            "Remaining Budget",
            f"₹{remaining}"
        )

        if total_expense > monthly_budget:

            st.error("Budget Exceeded ⚠️")

        elif total_expense > monthly_budget * 0.8:

            st.warning("80% Budget Used")

        else:

            st.success("Budget Under Control ✅")

    # ---------------- PREDICTIONS ----------------

    elif menu == "Predictions":

        st.title("🤖 AI Predictions")

        try:

            model = joblib.load(
                "expense_prediction_model.pkl"
            )

            future_days = st.slider(
                "Future Days",
                1,
                30,
                7
            )

            future = np.array([
                [len(expense_df) + future_days]
            ])

            prediction = model.predict(
                future
            )

            st.success(
                f"Predicted Expense: ₹{prediction[0]:.2f}"
            )

        except:

            st.warning(
                "Train ML model first."
            )

    # ---------------- SETTINGS ----------------

    elif menu == "Settings":

        st.title("⚙️ Settings")

        st.write("Settings Page")
