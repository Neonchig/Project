import sys
import bcrypt
import logging
import sqlite3

from fastapi import APIRouter, status

from Backend.models.user import User

router = APIRouter()
db = sqlite3.connect("/home/neonchig/app.db")
cursor = db.cursor()

@router.post("/register")
async def regUser(user: User):
    passwd = user.password.strip()
    logging.log(1, passwd)
    salt =  bcrypt.gensalt()
    password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                   (user.username, user.email, password.decode()))
    
    db.commit()
    db.close()
    return status.HTTP_201_CREATED