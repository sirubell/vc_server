# 1. install python packages
```
python -m pip install -r requirements.txt
```

# 2. .env file
繼驗證碼所需要的資訊還有SECRET字串放在在.env檔裡
如果在`vc_server.config.py`中設定`need_email_validation`為`False`就不用MAIL資訊
```bash
MAIL_USERNAME = <mail username>
MAIL_PASSWORD = <google app password>
MAIL_FROM = <mail username>
MAIL_PORT = "465"
MAIL_SERVER = smtp.gmail.com

# openssl rand -hex 32
SECRET =88436a0ddbb98b1cb8e61d48b1c484f6c9d9ffa2c4a445b4321c8256f9964b29 
```

# 3. Run
```bash
uvicorn vc_server.main:app --reload --host 0.0.0.0
```
