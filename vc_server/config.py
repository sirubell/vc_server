from dotenv import load_dotenv
import os

load_dotenv(".env")

conf = {
    "SECRET": os.getenv("SECRET"),
    "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
    "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
    "MAIL_FROM": os.getenv("MAIL_FROM"),
    "MAIL_PORT": int(os.getenv("MAIL_PORT")),
    "MAIL_SERVER": os.getenv("MAIL_SERVER"),
    "need_email_validation": False,
}
