import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import traceback # For detailed error logging

# .envファイルはこのdatabase.pyと同じ backend/ フォルダにあると想定
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
SSL_CA_PATH = os.getenv("SSL_CA_PATH")

# Validate required environment variables and show which ones are missing
required_vars = {
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}
missing = [name for name, value in required_vars.items() if not value]
if missing:
    missing_str = ", ".join(missing)
    raise ValueError(
        f"Missing required database environment variables: {missing_str}. "
        "Please check your .env or application settings."
    )

if not SSL_CA_PATH or not os.path.exists(SSL_CA_PATH):
    raise ValueError(
        f"SSL_CA_PATH '{SSL_CA_PATH}' is not set or the file does not exist. "
        "Azure MySQL requires SSL, please provide a valid CA certificate path."
    )

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# SSL接続設定: WorkbenchでCA証明書を指定したので、それをPyMySQLに渡す
# ssl_mode='VERIFY_CA' は、指定されたCAに対してサーバー証明書を検証することを意味します。
engine_args = {
    "connect_args": {
        "ssl": {
            "ca": SSL_CA_PATH,
            # "ssl_mode": "VERIFY_CA" # PyMySQL < 1.0.0 might not support ssl_mode directly in dict
                                     # For PyMySQL 1.0.0+ and MySQL Connector/Python, ssl_ca is enough for VERIFY_CA behavior by default
                                     # If specific ssl_mode is needed and supported:
                                     # "check_hostname": True # Recommended with VERIFY_CA
        }
    }
}
# PyMySQLのバージョンによっては、'ssl_ca': SSL_CA_PATH のような単純な指定で良い場合もあります。
# 'ssl': {'ca': SSL_CA_PATH} は一般的に受け入れられる形式です。
# Azure MySQLはデフォルトでSSLを強制し、信頼されたCAを使用しているため、
# クライアントがCAを指定して検証することで、中間者攻撃を防ぎます。

print(f"Attempting to connect to: {SQLALCHEMY_DATABASE_URL.replace(DB_PASSWORD, '********')}")
print(f"Using SSL CA certificate: {SSL_CA_PATH}")
print(f"Using engine arguments: {engine_args}")

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 接続テスト (アプリケーション起動時に確認用)
def test_db_connection():
    try:
        with engine.connect() as connection:
            print("Successfully connected to the database using SQLAlchemy engine!")
            return True
    except Exception as e:
        print(f"Failed to connect to the database using SQLAlchemy engine: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # このファイルが直接実行された場合に接続テストを行う
    if not DB_NAME:
        print("DB_NAME is not set in .env file. Please set it before testing.")
    elif not SSL_CA_PATH or not os.path.exists(SSL_CA_PATH):
        print(f"SSL_CA_PATH '{SSL_CA_PATH}' is not valid. Please check .env and file existence.")
    elif test_db_connection():
        print("Database connection test successful.")
    else:
        print("Database connection test failed.")
