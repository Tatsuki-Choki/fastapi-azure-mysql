from sqlalchemy import create_engine

import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')  # デフォルトのMySQLポート番号を指定
DB_NAME = os.getenv('DB_NAME', 'test_db')

# 環境変数のデバッグ出力
print(f"DB_USER: {DB_USER}")
print(f"DB_HOST: {DB_HOST}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_NAME: {DB_NAME}")

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SSL_CA_PATH = os.getenv('SSL_CA_PATH', '')

# エンジンの作成
connect_args = {}
if SSL_CA_PATH and os.path.exists(SSL_CA_PATH):
    print(f"Using SSL CA certificate: {SSL_CA_PATH}")
    connect_args = {
        "ssl_ca": SSL_CA_PATH
    }
else:
    print("No SSL CA certificate specified or file not found, connecting without SSL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=connect_args
)
