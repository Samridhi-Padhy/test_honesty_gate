def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email

def get_user_email(user: dict | None) -> str:
    if user is None: return "unknown@example.com"
    return user.get("email", "unknown@example.com")
