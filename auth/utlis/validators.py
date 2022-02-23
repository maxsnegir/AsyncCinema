from email_validator import validate_email, EmailNotValidError


def email_validator(email: str):
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise e
    return email
