import sys
import bcrypt
import sqlite3

from fastapi import APIRouter, status

sys.path.append("/home/neonchig/Documents/Project/Source/Backend/models")

from user import User # type: ignore

router = APIRouter()
conn = sqlite3.connect("/home/neonchig/app.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

@router.post("/login")
def login(user: User):

    passwd = user.password.strip()

    cursor.execute(f"SELECT * FROM users WHERE username=\"{user.username}\"")
    row = cursor.fetchone()

    res = dict(row)

    hashedPasswd = res["password"]

    if bcrypt.checkpw(str.encode(user.password), str.encode(hashedPasswd)):
        return status.HTTP_200_OK

    return status.HTTP_401_UNAUTHORIZED