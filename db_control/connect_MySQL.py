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

# 証明書ファイルのパスを直接指定（backend直下にあるファイルを参照）
import pathlib

# 現在のファイルからの相対パスで証明書を指定
current_dir = pathlib.Path(__file__).parent.parent  # backend ディレクトリ
SSL_CA_PATH = current_dir / "DigiCertGlobalRootCA.crt.pem"

# エンジンの作成
connect_args = {}
if os.path.exists(SSL_CA_PATH):
    print(f"Using SSL CA certificate: {SSL_CA_PATH}")
    connect_args = {
        "ssl_ca": str(SSL_CA_PATH)
    }
else:
    print("SSL CA certificate file not found, connecting without SSL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=connect_args
)
