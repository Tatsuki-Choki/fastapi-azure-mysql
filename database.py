import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import traceback # For detailed error logging
import pathlib

# .envファイルはこのdatabase.pyと同じ backend/ フォルダにあると想定
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 証明書ファイルのパスを直接指定（backend直下にあるファイル）
current_dir = pathlib.Path(__file__).parent  # database.pyがあるディレクトリ（backend）
SSL_CA_PATH = current_dir / "DigiCertGlobalRootCA.crt.pem"

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError(
        "Database connection information (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD) "
        "is missing or incomplete in .env file. Please check."
    )

if not os.path.exists(SSL_CA_PATH):
    raise ValueError(
        f"SSL Certificate file '{SSL_CA_PATH}' does not exist. "
        "Azure MySQL requires SSL, please ensure the certificate file is present."
    )

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# SSL接続設定: backend直下にある証明書ファイルを使用
# ssl_mode='VERIFY_CA' は、指定されたCAに対してサーバー証明書を検証することを意味します。
engine_args = {
    "connect_args": {
        "ssl": {
            "ca": str(SSL_CA_PATH),  # Path型からstr型に変換
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
    elif not os.path.exists(SSL_CA_PATH):
        print(f"SSL Certificate file '{SSL_CA_PATH}' does not exist. Please check file existence.")
    elif test_db_connection():
        print("Database connection test successful.")
    else:
        print("Database connection test failed.")
