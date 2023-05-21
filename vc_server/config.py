from dotenv import load_dotenv
import os

load_dotenv(".env")


mail_username = os.getenv("MAIL_USERNAME")
mail_password = os.getenv("MAIL_PASSWORD")
mail_from = os.getenv("MAIL_FROM")
mail_port = int(os.getenv("MAIL_PORT"))
mail_server = os.getenv("MAIL_SERVER")
secret = os.getenv("SECRET")
algorithm = "HS256"
access_token_expire_minutes = 30
need_email_validation = False
