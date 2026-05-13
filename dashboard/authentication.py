import json
import os
from passlib.context import CryptContext

# ✅ Use PBKDF2 instead of bcrypt to avoid bcrypt backend/version issues
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

USERS_PATH = os.path.join("data", "users.json")

MIN_PASSWORD_LEN = 6
MAX_PASSWORD_LEN = 128  # safe for PBKDF2


def _ensure_users_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(USERS_PATH):
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)


def load_users() -> dict:
    _ensure_users_file()
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users: dict) -> None:
    _ensure_users_file()
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def normalize_phone(phone: str) -> str:
    return "".join(ch for ch in (phone or "") if ch.isdigit())


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def signup(name: str, phone: str, password: str) -> tuple[bool, str]:
    name = (name or "").strip()
    phone_n = normalize_phone(phone)
    password = password or ""

    if not name:
        return False, "Name is required."
    if len(phone_n) < 8:
        return False, "Enter a valid phone number."
    if len(password) < MIN_PASSWORD_LEN:
        return False, f"Password must be at least {MIN_PASSWORD_LEN} characters."
    if len(password) > MAX_PASSWORD_LEN:
        return False, f"Password must be at most {MAX_PASSWORD_LEN} characters."

    users = load_users()
    if phone_n in users:
        return False, "This phone number is already registered."

    users[phone_n] = {
        "name": name,
        "phone": phone_n,
        "password_hash": hash_password(password),
    }
    save_users(users)
    return True, "Account created successfully. Please login."


def login(phone: str, password: str) -> tuple[bool, str, dict | None]:
    phone_n = normalize_phone(phone)
    password = password or ""

    users = load_users()
    if phone_n not in users:
        return False, "User not found. Please sign up.", None

    user = users[phone_n]
    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password.", None

    return True, "Login successful.", user
