from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json


# database.py からインポート (同じディレクトリにあると仮定)
from database import engine, Base, get_db, test_db_connection # test_db_connection を追加
from sqlalchemy.orm import Session # Session をインポート
import models # SQLAlchemyモデルをインポート

# データベーステーブルを作成
models.Base.metadata.create_all(bind=engine)

class Customer(BaseModel): # これはPydanticモデルです
    customer_id: str
    customer_name: str
    age: int
    gender: str


app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("FastAPI application startup...")
    if test_db_connection(): # 起動時に接続テスト
        print("Database connection successful on startup.")
    else:
        print("DATABASE CONNECTION FAILED ON STARTUP. Please check logs and .env settings.")
        # 本番環境などでは、ここでアプリケーションを停止させることも検討できます
        # raise RuntimeError("Failed to connect to the database on startup.")



@app.get("/")
def index():
    return {"message": "FastAPI top page!"}


# @app.post("/customers") # このエンドポイントは現状DBとは連携していません
# def create_customer(customer: Customer):
#     print(f"Received customer: {customer}")
#     return {"message": "Customer received (not saved to DB yet)", "customer_data": customer}

# 以下はデータベースと連携するエンドポイントの例です。
# SQLAlchemyモデル (例: models.Customer) が別途必要になります。

# from . import models # models.py があると仮定
# from . import schemas # schemas.py (Pydanticモデル) があると仮定

# @app.post("/customers_db/", response_model=schemas.Customer) # schemas.CustomerもPydanticモデル
# def create_customer_in_db(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
#     # return crud.create_customer(db=db, customer=customer) # crud.pyに関数を定義
#     pass # 実装待ち

# @app.get("/customers_db/{customer_id}", response_model=schemas.Customer)
# def read_customer_from_db(customer_id: str, db: Session = Depends(get_db)):
#     # db_customer = crud.get_customer(db, customer_id=customer_id)
#     # if db_customer is None:
#     #     raise HTTPException(status_code=404, detail="Customer not found")
#     # return db_customer
#     pass # 実装待ち

@app.post("/customers")
def create_customer(customer: Customer, db: Session = Depends(get_db)):
    print(f"Creating customer: {customer}")
    
    # 既存の customer_id をチェック
    existing_customer = db.query(models.Customer).filter(models.Customer.customer_id == customer.customer_id).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer ID already exists")
    
    # 新しい顧客をデータベースに保存
    new_db_customer = models.Customer(
        customer_id=customer.customer_id,
        customer_name=customer.customer_name,
        age=customer.age,
        gender=customer.gender
    )
    db.add(new_db_customer)
    db.commit()
    db.refresh(new_db_customer)
    
    return {
        "message": "Customer created successfully",
        "customer": {
            "id": new_db_customer.id,
            "customer_id": new_db_customer.customer_id,
            "customer_name": new_db_customer.customer_name,
            "age": new_db_customer.age,
            "gender": new_db_customer.gender
        }
    }


@app.get("/customers_one")
def read_one_customer(customer_id: str = Query(...), db: Session = Depends(get_db)):
    print(f"Reading customer_id: {customer_id} from database")
    
    db_customer = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "message": "Customer retrieved successfully",
        "customer": {
            "id": db_customer.id,
            "customer_id": db_customer.customer_id,
            "customer_name": db_customer.customer_name,
            "age": db_customer.age,
            "gender": db_customer.gender
        }
    }


@app.get("/allcustomers")
def read_all_customer(db: Session = Depends(get_db)):
    print("Reading all customers from database")
    customers = db.query(models.Customer).all()
    
    return {
        "message": "All customers retrieved successfully",
        "customers": [
            {
                "id": customer.id,
                "customer_id": customer.customer_id,
                "customer_name": customer.customer_name,
                "age": customer.age,
                "gender": customer.gender
            }
            for customer in customers
        ]
    }


@app.put("/customers")
def update_customer(customer: Customer, db: Session = Depends(get_db)):
    print(f"Updating customer: {customer}")
    
    db_customer = db.query(models.Customer).filter(models.Customer.customer_id == customer.customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # 顧客情報を更新
    db_customer.customer_name = customer.customer_name
    db_customer.age = customer.age
    db_customer.gender = customer.gender
    
    db.commit()
    db.refresh(db_customer)
    
    return {
        "message": "Customer updated successfully",
        "customer": {
            "id": db_customer.id,
            "customer_id": db_customer.customer_id,
            "customer_name": db_customer.customer_name,
            "age": db_customer.age,
            "gender": db_customer.gender
        }
    }


@app.delete("/customers")
def delete_customer(customer_id: str = Query(...), db: Session = Depends(get_db)):
    print(f"Deleting customer_id: {customer_id} from database")
    
    db_customer = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # 顧客を削除
    db.delete(db_customer)
    db.commit()
    
    return {
        "message": "Customer deleted successfully",
        "customer_id": customer_id,
        "status": "deleted"
    }


@app.get("/fetchtest")
def fetchtest():
    response = requests.get('https://jsonplaceholder.typicode.com/users')
    return response.json()
