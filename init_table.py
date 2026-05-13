from app.database import engine
from app.base import Base
from app.models.user import User
from app.models.service import Service

from sqlalchemy import inspect

def init_db():
    Base.metadata.create_all(bind=engine)
    print("tables created successfully")

init_db()
print(inspect(engine).get_table_names())