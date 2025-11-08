import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from models import Base

load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(db_url)

#try:
#    conn = engine.connect()
#    Base.metadata.drop_all(engine)
#    Base.metadata.create_all(engine)
#except Exception as e:
#    print(e)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

