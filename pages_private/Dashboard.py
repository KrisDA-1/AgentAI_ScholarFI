import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from utils.auth import require_login
from utils.styles import load_css
from services.discounts_service import get_top_discounts
from database.db_methods import get_transactions, get_goals
from pages_private.AI_Coach import run as coach_run
from services.savings_recomender import generate_savings_recommendations

def run():
    # --- SESSION AUTH CHECK ---
    require_login()
    user_id = st.session_state.user_id
    name = st.session_state.user_name

    # --- Load CSS ---
    load_css()

    # --- Fetch Data ---
    transactions = get_transactions(user_id)
    goals = get_goals(user_id)

    # --- Financial Metrics ---
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    total_balance = total_income - total_expense
    total_savings = sum(g['current_amount'] for g in goals)

    # --- PAGE SETTINGS ---
    st.set_page_config(page_title="ScholarFi Dashboard", layout="wide", page_icon="💷")

    # --- HEADER ---
    st.markdown(
        f"<div class='header-section'><h1>Welcome back, {name}</h1><p>It is the best time to manage your finances</p></div>", 
        unsafe_allow_html=True
    )

    # --- METRICS ---
    col1, col2, col3, col4 = st.columns(4)
    metrics = [("Total Balance", total_balance), ("Income", total_income),
               ("Expenses", total_expense), ("Total Savings", total_savings)]
    
    for col, (label, value) in zip([col1, col2, col3, col4], metrics):
        col.markdown(f"<div class='metric-card'><h3>{label}</h3><h2>£{value}</h2></div>", unsafe_allow_html=True)

    # # --- WARNINGS ---
    # st.markdown("<div class='alert-warning'>You spent £22 more on Food this week. Consider cooking 2 more days to save £15.</div>", unsafe_allow_html=True)

    # # AI COACH SECTION
    # @st.dialog("🤖 Financial Coach") 
    # def show_coach_modal():
    #     coach_run()
    # if st.button("Ask My Financial Coach"):
    #     show_coach_modal() 

    # --- MAIN CONTENT ---
    col1, col2 = st.columns([1, 1])

   # --- Money Flow Chart ---
    with col1:
        st.markdown("<div class='section-card'><h3>Money Flow</h3>", unsafe_allow_html=True)
        df = pd.DataFrame(transactions)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            # Pivot table por tipo
            df_long = df.pivot_table(
                index=df['date'].dt.month,  # Usamos número de mes para ordenar
                columns='type',
                values='amount',
                aggfunc='sum'
            ).fillna(0).reset_index()
            # Solo columnas existentes
            columns_to_melt = [col for col in ['income', 'expense'] if col in df_long.columns]
            if columns_to_melt:
                df_long = df_long.melt(
                    id_vars='date',  # aquí 'date' es el número de mes
                    value_vars=columns_to_melt,
                    var_name='Type',
                    value_name='Amount'
                )
                # Mapeamos número de mes a nombre de mes para mostrar
                month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                            7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
                df_long['Month'] = df_long['date'].map(month_names)
                # --- Chart ---
                chart = alt.Chart(df_long).mark_bar().encode(
                    x=alt.X("Month:N", sort=list(month_names.values())),  # orden correcto
                    y="Amount:Q",
                    color=alt.Color("Type:N", scale=alt.Scale(range=["#dd6548", "#faf0ee"])),
                    tooltip=["Month", "Type", "Amount"]
                ).properties(height=300)
                st.altair_chart(chart, width="stretch")
            else:
                st.info("No transactions yet.")
        else:
            st.info("No transactions yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Store Discounts ---
    with col2:
        st.markdown("<div class='section-card'><h3>Discounts</h3>", unsafe_allow_html=True)
        has_expenses = any(t['type'] == 'expense' for t in transactions)
        if not has_expenses:
            st.info("No expenses yet.")
        else:
            try:
                category_to_query = {
                    "Groceries": "groceries",
                    "Health & Beauty": "health+beauty",
                    "Cleaning": "cleaning",
                    "Online Shopping": "online+shopping",
                    "Others": "other"
                }
                user_categories = set(t['category'] for t in transactions if t['type'] == 'expense' and t['category'] in category_to_query)
                queries = [category_to_query[cat] for cat in user_categories] if user_categories else ["groceries"]
                user_context = {}
                
                # Add snippet while loading discounts
                loading_msg = st.empty()
                loading_msg.markdown('<div style="color: #d71f59; font-size: 1em; font-weight: bold;">🔍 ScholarFi is analyzing the best offers according to your spends...</div>', unsafe_allow_html=True)
                discounts = get_top_discounts(queries, user_context)
                loading_msg.empty() 
                
                if not discounts:
                    st.markdown("<div class='alert-warning'>No discounts available right now.</div>", unsafe_allow_html=True)
                else:
                    for d in discounts[:5]:
                        st.markdown(f"<div class='alert-warning'>{d.get('text', '')}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading discounts: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # --- Recent Transactions & Pie Chart ---
    col1, col2, col3 = st.columns([1.5, 1.25, 1])

    with col1:
        st.markdown("<div class='section-card'><h3>Recent Transactions</h3>", unsafe_allow_html=True)
        if transactions:
            # Convert to DataFrame
            df_trans = pd.DataFrame(transactions)
            df_trans = df_trans[['amount', 'category', 'date', 'type']]
            # Ensure 'amount' is numeric and round to 2 decimals
            df_trans['amount'] = df_trans['amount'].astype(float).round(2)
            # Last 5 transactions sorted by date
            df_trans = df_trans.sort_values(by='date', ascending=False).head(5)
            
            # Function to color 'amount' based on 'type' (returns a Series with styles for each column)
            def color_amount(row):
                styles = pd.Series('', index=row.index)  # Empty Series with same columns
                if row['type'] == 'income':
                    styles['amount'] = 'color: green; font-weight:600'
                elif row['type'] == 'expense':
                    styles['amount'] = 'color: red; font-weight:600'
                return styles
            
            # Apply formatting to 2 decimals and then coloring to amount column based on type
            styled_df = df_trans.style.format({'amount': '{:.2f}'}).apply(color_amount, axis=1)
            st.dataframe(styled_df)
        else:
            st.info("No transactions yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        current_month_name = pd.Timestamp.now().strftime("%B")
        st.markdown(f"<div class='section-card'><h3>Expense Breakdown {current_month_name}</h3>", unsafe_allow_html=True)
        df = pd.DataFrame(transactions)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date']) # Date conversion
            df = df[df['type'] == 'expense'] # Filter only expenses
            # Filter actual month
            current_month = pd.Timestamp.now().month
            current_year = pd.Timestamp.now().year
            df = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]

            if df.empty:
                st.info("No expenses recorded this month.")
            else:
                df_grouped = df.groupby("category")["amount"].sum().reset_index() # Grouped by category
                # Create the Pie Chart
                pie = alt.Chart(df_grouped).mark_arc().encode(
                    theta=alt.Theta("amount:Q", title="Amount"),
                    color=alt.Color("category:N", title="Category"),
                    tooltip=["category", "amount"]
                ).properties(height=280)
                st.altair_chart(pie, width="stretch")
        else:
            st.info("No transactions yet.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='section-card-empty'><h3></h3>", unsafe_allow_html=True)
        
        if 'df_grouped' in locals() and not df_grouped.empty:
            # Show list of expenses by category
            total_amount = df_grouped['amount'].sum()
            for _, row in df_grouped.iterrows():
                # calcular el porcentaje para cada fila
                percent = (row["amount"] / total_amount) * 100

                st.markdown(
                    f"<div class=''><strong>{row['category']}</strong>: "
                    f"£{row['amount']:.2f} ({percent:.1f}%)</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No expenses to display.")
            
    # --- Saving Goals ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='section-card'><h3>Personalized Savings Tips</h3>", unsafe_allow_html=True)
        recommendations = generate_savings_recommendations(transactions, goals)
        for r in recommendations:
            st.markdown(f"<div class='alert-warning'>{r['text']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-card'><h3>Savings Goals</h3>", unsafe_allow_html=True)
        if goals:
            for g in goals:
                filled = int((g['current_amount'] / g['target_amount']) * 100) if g['target_amount'] > 0 else 0
                
                st.markdown(f"""
                    <div class="goal-header">
                        <span>{g['name']}</span>
                        <span>{filled}%</span>
                    </div>
                    <div class="custom-progress">
                        <div class="custom-progress-fill" style="width:{filled}%"></div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No savings goals yet. Add them in Finance Hub.")
        st.markdown("</div>", unsafe_allow_html=True)

