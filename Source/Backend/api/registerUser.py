import sys

sys.path.append("/home/neonchig/Documents/Project/Source/Backend/models")

import bcrypt
import logging
import sqlite3

from user import User # type: ignore
from fastapi import APIRouter, status

router = APIRouter()
db = sqlite3.connect("/home/neonchig/app.db")
cursor = db.cursor()

@router.post("/reg")
async def regUser(user: User):
    passwd = user.password.strip()
    logging.log(1, passwd)
    salt =  bcrypt.gensalt()
    password = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                   (user.username, password.decode()))
    db.commit()
    db.close()
    return status.HTTP_201_CREATED