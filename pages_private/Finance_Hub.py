import streamlit as st
from datetime import date
from pathlib import Path
from utils.auth import require_login
from utils.styles import load_css
from database.db_methods import ( get_user, update_user_info, 
    add_transaction, create_goal, add_to_goal, get_goals)
from pages_public.Register import is_strong_password

def run():
    # --- SESSION AUTH CHECK ---
    require_login()
    user_id = st.session_state.user_id

    st.set_page_config(page_title="Finance Hub", layout="wide")
    load_css()

    # --- HEADER ---
    st.markdown(
        "<div class='header-section'><h1>Finance Hub</h1><p>Manage your personal info, transactions, and goals</p></div>",
        unsafe_allow_html=True
    )

    # --- PERSONAL INFORMATION ---
    st.markdown("<div class='section-card'><h3>👤 Personal Information</h3></div>", unsafe_allow_html=True)
    user_data = get_user(user_id)
    name = st.text_input("Name", value=user_data.get("name", ""), key="user_name")
    email = st.text_input("Email", value=user_data.get("email", ""), key="user_email", disabled=True)
    new_password = st.text_input("New Password", type="password", key="new_password")

    if st.button("Update Personal Information"):
        if not name.strip():
            st.warning("Name cannot be empty.")
        elif not is_strong_password(new_password):
            st.warning("Password must be at least 8 characters long and include at least 1 letter, 1 number, and 1 special character.")
        else:
            success = update_user_info(user_id, name=name, password=new_password)
            if success:
                st.success("Personal information updated successfully!")
            else:
                st.error("Error updating information.")

    # --- ACCOUNT TRANSACTIONS ---
    st.markdown("<div class='section-card'><h3>💷 Account Transactions</h3></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Función auxiliar para transacciones
    def handle_transaction(is_income=True):
        amount_key = "deposit" if is_income else "spend"
        date_key = "deposit_date" if is_income else "spend_date"
        note_key = "spend_note"
        category_key = "spend_cat"
        btn_key = "btn_add" if is_income else "btn_spend"
        trans_type = "income" if is_income else "expense"

        amount = st.number_input("Amount (£)", min_value=0.0, step=1.0, key=amount_key)
        trans_date = st.date_input("Date", value=date.today(), key=date_key, max_value=date.today())

        if not is_income:
            category = st.selectbox("Category", ["Groceries", "Health & Beauty", "Cleaning", "Online Shopping", "Others"], key=category_key)
            note = st.text_input("Note (optional)", key=note_key)
        else:
            category, note = "Deposit", ""

        if st.button("Add Money" if is_income else "Record Expense", key=btn_key):
            if amount <= 0:
                st.warning("Amount must be greater than £0!")
            else:
                add_transaction(user_id, amount, category, note, trans_date, trans_type)
                st.success(f"{'£'+str(amount)+' added' if is_income else 'Expense of £'+str(amount)+' recorded'} on {trans_date}!")

    with col1:
        st.markdown("**Add Money to Account**")
        handle_transaction(is_income=True)

    with col2:
        st.markdown("**Spend / Withdraw Money**")
        handle_transaction(is_income=False)

    # --- SAVINGS GOALS ---
    st.markdown("<div class='section-card'><h3>🎯 Savings Goals Management</h3></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Crear nueva meta
    with col1:
        st.markdown("**Create New Goal**")
        goal_name = st.text_input("Goal Name", key="goal_name")
        goal_amount = st.number_input("Target Amount (£)", min_value=0.0, key="goal_amount")
        deadline = st.date_input("Deadline", key="goal_deadline", min_value=date.today())

        if st.button("Create Goal", key="btn_create_goal"):
            if not goal_name.strip():
                st.warning("Goal name cannot be empty.")
            elif goal_amount <= 0:
                st.warning("Goal amount must be greater than zero.")
            else:
                create_goal(user_id, goal_name, goal_amount, deadline)
                st.success(f"Goal '{goal_name}' created successfully!")

    # Añadir dinero a meta existente
    with col2:
        st.markdown("**Add Money to Existing Goal**")
        goals = get_goals(user_id)
        if goals:
            selected_goal = st.selectbox("Select Goal", [g['name'] for g in goals], key="select_goal")
            add_amount = st.number_input("Amount to Add (£)", min_value=0.0, key="add_to_goal")
            if st.button("Add to Goal", key="btn_add_goal"):
                if add_amount <= 0:
                    st.warning("Amount to add must be greater than £0!")
                else:
                    goal_id = next((g['id'] for g in goals if g['name'] == selected_goal), None)
                    if goal_id:
                        add_to_goal(goal_id, add_amount, date.today())
                        st.success(f"£{add_amount} added to '{selected_goal}'!")
                    else:
                        st.error("Goal not found. Operation failed.")
        else:
            st.info("You have no savings goals yet. Create one first.")
            
    st.markdown("</div>", unsafe_allow_html=True)
