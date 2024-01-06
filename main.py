from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  

DATABASE_URL = "mysql+mysqlconnector://root:root@localhost:8889/test_db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str
    
class RegisterRequest(BaseModel):
    username: str
    password: str

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String)
    
Base.metadata.create_all(bind=engine)

class UserInDB(User):
    class Config:
        orm_mode = True
        
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# post for check username and password to login
@app.post("/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)) :
    user = db.query(User).filter(User.username == login_data.username, User.password == login_data.password).first()
    if user:
        return {"message":"Login successful"}
    else:
        return {"message":"Login failed"}

# post for get username and password append to database
@app.post('/register')
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == register_data.username).first()
    if existing_user:
        return {'message':'Username already registered'}
    
    new_user = User(username=register_data.username, password=register_data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message":"Register successful"}