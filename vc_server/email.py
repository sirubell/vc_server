from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

import random
from .config import conf

conf = ConnectionConfig(
    MAIL_USERNAME=conf["MAIL_USERNAME"],
    MAIL_PASSWORD=conf["MAIL_PASSWORD"],
    MAIL_FROM=conf["MAIL_FROM"],
    MAIL_PORT=int(conf["MAIL_PORT"]),
    MAIL_SERVER=conf["MAIL_SERVER"],
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

prefix = " 驗證碼："


def generate_validation_code():
    code = ""
    for i in range(5):
        code += str(random.randrange(0, 10))
    return code


async def send_email(email_to: str, code: str):
    message = MessageSchema(
        subject="視覺密碼門鎖系統信箱驗證",
        recipients=[email_to],
        body=prefix + code,
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
