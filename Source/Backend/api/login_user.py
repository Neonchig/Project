import sqlite3

import bcrypt
from fastapi import APIRouter, status

from Source.Backend.models.user import Login_user

router = APIRouter()
conn = sqlite3.connect("/home/neonchig/app.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

@router.post("/login")
def login(user: Login_user):

    if not(user.email or user.username):
        return status.HTTP_422_UNPROCESSABLE_CONTENT

    if user.username:
        cursor.execute('SELECT * FROM users WHERE username = ?', [user.username])
        row = cursor.fetchone()
    else:
        cursor.execute('SELECT * FROM users WHERE email = ?', [user.email])
        row = cursor.fetchone()

    if row:
        res = dict(row)
    else:
        return status.HTTP_404_NOT_FOUND

    hashedPasswd = res["password"]

    if bcrypt.checkpw(str.encode(user.password), str.encode(hashedPasswd)):
        return status.HTTP_200_OK

    return status.HTTP_401_UNAUTHORIZED
