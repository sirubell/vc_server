from dotenv import load_dotenv
import os

load_dotenv(".env")


mail_username = os.getenv("MAIL_USERNAME")
mail_password = os.getenv("MAIL_PASSWORD")
mail_from = os.getenv("MAIL_FROM")
mail_port = int(os.getenv("MAIL_PORT"))
mail_server = os.getenv("MAIL_SERVER")
secret = os.getenv("SECRET")
algorithm = os.getenv("ALGORITHM")
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
need_email_validation = os.getenv("EMAIL_VALIDATION", "false").lower() in (
    "true",
    "1",
    "t",
)
