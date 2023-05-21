from fastapi import FastAPI

from vc_server.routers import users, doors, admin, helpers, auth
from vc_server.database import database, models

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(doors.router)
app.include_router(admin.router)
app.include_router(helpers.router)
