from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

import random
from vc_server import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.mail_username,
    MAIL_PASSWORD=config.mail_password,
    MAIL_FROM=config.mail_from,
    MAIL_PORT=config.mail_port,
    MAIL_SERVER=config.mail_server,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


def generate_validation_code():
    code = ""
    for i in range(5):
        code += str(random.randrange(0, 10))
    return code


async def send_email(email_to: str, code: str):
    prefix = " 驗證碼："
    message = MessageSchema(
        subject="視覺密碼門鎖系統信箱驗證",
        recipients=[email_to],
        body=prefix + code,
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
