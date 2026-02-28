import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

load_dotenv()

db_back_user = os.getenv('DB_BACK_USER')
db_back_password = quote_plus(os.getenv('DB_BACK_PASSWORD', ''))
db_back_host = os.getenv('DB_BACK_HOST')
db_back_port = os.getenv('DB_BACK_PORT')
db_back_name = os.getenv('DB_BACK_NAME')

db_front_user = os.getenv('DB_FRONT_USER')
db_front_password = quote_plus(os.getenv('DB_FRONT_PASSWORD', ''))
db_front_host = os.getenv('DB_FRONT_HOST')
db_front_port = os.getenv('DB_FRONT_PORT')
db_front_name = os.getenv('DB_FRONT_NAME')

db_back_url = f"postgresql+psycopg2://{db_back_user}:{db_back_password}@{db_back_host}:{db_back_port}/{db_back_name}?client_encoding=utf8"
db_front_url = f"postgresql+psycopg2://{db_front_user}:{db_front_password}@{db_front_host}:{db_front_port}/{db_front_name}?client_encoding=utf8"

engine = create_engine(db_back_url)
front_engine = create_engine(db_front_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
FrontSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=front_engine)

