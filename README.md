# Run
```bash
uvicorn vc_server.main:app --reload --host 0.0.0.0
```
# .env file
寄信還有SECRET字串藏在.env檔裡
```bash
MAIL_USERNAME = <mail username>
MAIL_PASSWORD = <google app password>
MAIL_FROM = <mail username>
MAIL_PORT = "465"
MAIL_SERVER = smtp.gmail.com

SECRET = 1234895473985473895 # 之類的東西
```
