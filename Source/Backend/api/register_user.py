import sqlite3

import bcrypt
from fastapi import APIRouter, status

from Source.Backend.models.user import User

router = APIRouter()
db = sqlite3.connect("/home/neonchig/app.db")
cursor = db.cursor()

@router.post("/register")
async def regUser(user: User):
    # passwd = user.password.strip()
    salt =  bcrypt.gensalt()
    password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                   (user.username, user.email, password.decode()))

    db.commit()
    db.close()
    return status.HTTP_201_CREATED
