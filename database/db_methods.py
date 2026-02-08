# database/db_methods.py
import psycopg2
import bcrypt
from database.database import get_connection

# ---------------- USERS ----------------
def create_user(name, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id",
            (name, email, hashed_pw)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
    except psycopg2.Error:
        conn.close()
        return None

    conn.close()
    return user_id


def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "password": row[3]}
    return None


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password FROM users WHERE email=%s", (email,))
    row = cursor.fetchone()
    conn.close()
    return row


def update_user_info(user_id, name=None, password=None):
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    values = []

    if name:
        updates.append("name=%s")
        values.append(name)
    if password:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        updates.append("password=%s")
        values.append(hashed_pw)

    if not updates:
        conn.close()
        return False

    values.append(user_id)
    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id=%s", values)
    conn.commit()
    conn.close()
    return True


def verify_user(email, password):
    user = get_user_by_email(email)
    if user:
        hashed_pw = user[3]
        if bcrypt.checkpw(password.encode(), hashed_pw.tobytes() if hasattr(hashed_pw, 'tobytes') else hashed_pw):
            return {"id": user[0], "name": user[1], "email": user[2]}
    return None


# ---------------- TRANSACTIONS ----------------
def add_transaction(user_id, amount, category, note, date, type_):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, category, note, date, type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, amount, category, note, date, type_))
    conn.commit()
    conn.close()


def get_transactions(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, amount, category, note, date, type
        FROM transactions
        WHERE user_id=%s
        ORDER BY date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "amount": r[1], "category": r[2], "note": r[3], "date": r[4], "type": r[5]}
        for r in rows
    ]


# ---------------- GOALS ----------------
def create_goal(user_id, name, target_amount, deadline):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO goals (user_id, name, target_amount, deadline)
        VALUES (%s, %s, %s, %s)
    """, (user_id, name, target_amount, deadline))
    conn.commit()
    conn.close()


def add_to_goal(goal_id, amount, date_):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals SET current_amount = current_amount + %s WHERE id=%s",
        (amount, goal_id)
    )
    conn.commit()
    conn.close()


def get_goals(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, target_amount, current_amount, deadline FROM goals WHERE user_id=%s",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "target_amount": r[2], "current_amount": r[3], "deadline": r[4]}
        for r in rows
    ]


# import sqlite3
# import bcrypt
# from database.database import get_connection

# # ---------------- USERS ----------------
# def create_user(name, email, password):
#     conn = get_connection()
#     cursor = conn.cursor()
#     hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
#     try:
#         cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
#                        (name, email, hashed_pw))
#         conn.commit()
#         user_id = cursor.lastrowid
#     except sqlite3.IntegrityError:
#         conn.close()
#         return None  # email ya existe
#     conn.close()
#     return user_id

# def get_user(user_id):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
#     row = cursor.fetchone()
#     conn.close()
#     if row:
#         return {"id": row[0], "name": row[1], "email": row[2], "password": row[3]}
#     return None

# def get_user_by_email(email):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM users WHERE email=?", (email,))
#     row = cursor.fetchone()
#     conn.close()
#     return row

# def update_user_info(user_id, name=None, password=None):
#     conn = get_connection()
#     cursor = conn.cursor()
#     updates = []
#     values = []

#     if name:
#         updates.append("name=?")
#         values.append(name)
#     if password:
#         hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
#         updates.append("password=?")
#         values.append(hashed_pw)

#     if not updates:
#         conn.close()
#         return False

#     values.append(user_id)
#     cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id=?", values)
#     conn.commit()
#     conn.close()
#     return True

# def verify_user(email, password):
#     user = get_user_by_email(email)
#     if user:
#         hashed_pw = user[3]
#         if isinstance(hashed_pw, str):
#             hashed_pw = hashed_pw.encode("utf-8")
#         if bcrypt.checkpw(password.encode(), hashed_pw):
#             return {"id": user[0], "name": user[1], "email": user[2]}
#     return None

# # ---------------- TRANSACTIONS ----------------
# def add_transaction(user_id, amount, category, note, date, type_):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO transactions (user_id, amount, category, note, date, type) VALUES (?, ?, ?, ?, ?, ?)",
#                    (user_id, amount, category, note, date, type_))
#     conn.commit()
#     conn.close()

# def get_transactions(user_id):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, amount, category, note, date, type FROM transactions WHERE user_id=? ORDER BY date DESC", (user_id,))
#     rows = cursor.fetchall()
#     conn.close()
#     return [{"id": r[0], "amount": r[1], "category": r[2], "note": r[3], "date": r[4], "type": r[5]} for r in rows]

# # ---------------- GOALS ----------------
# def create_goal(user_id, name, target_amount, deadline):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO goals (user_id, name, target_amount, deadline) VALUES (?, ?, ?, ?)",
#                    (user_id, name, target_amount, deadline))
#     conn.commit()
#     conn.close()

# def add_to_goal(goal_id, amount, date_):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("UPDATE goals SET current_amount = current_amount + ? WHERE id=?", (amount, goal_id))
#     conn.commit()
#     conn.close()

# def get_goals(user_id):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, name, target_amount, current_amount, deadline FROM goals WHERE user_id=?", (user_id,))
#     rows = cursor.fetchall()
#     conn.close()
#     return [{"id": r[0], "name": r[1], "target_amount": r[2], "current_amount": r[3], "deadline": r[4]} for r in rows]
