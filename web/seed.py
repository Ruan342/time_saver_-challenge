import os

from werkzeug.security import generate_password_hash

from db import get_connection, init_db


def seed_test_user():
    email = os.environ.get("TEST_USER_EMAIL", "teste@timesaver.com")
    password = os.environ.get("TEST_USER_PASSWORD", "teste123")

    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (email,)
    ).fetchone()

    if existing is None:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (email, generate_password_hash(password, method="pbkdf2:sha256")),
        )
        conn.commit()

    conn.close()


if __name__ == "__main__":
    init_db()
    seed_test_user()
