from app.db.session import get_db_connection

def save_message(message):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO messages (full_name, email, subject, message)
            VALUES (%s, %s, %s, %s)
        """, (
            message.full_name,
            message.email,
            message.subject,
            message.message
        ))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print("Error saving message:", e)
        return False

    finally:
        cur.close()
        conn.close()
