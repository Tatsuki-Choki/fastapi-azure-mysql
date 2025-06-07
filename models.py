from sqlalchemy import Column, Integer, String
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)

    def __repr__(self):
        return f"<Customer(id={self.id}, customer_id='{self.customer_id}', customer_name='{self.customer_name}', age={self.age}, gender='{self.gender}')>"
