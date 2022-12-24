"""
Helpful utils
"""
import re
from urllib.parse import urlparse

import bcrypt
from dataclasses import dataclass


@dataclass
class UsernameType:
    email = "EMAIL"
    phone = "PHONE"
    regular = "REGULAR"


class SQLInjectionError(ValueError):

    def __init__(self, string: str) -> None:
        self._string = string

    def __str__(self):
        return f"String {self._string} contain or may contain SQL script"


async def check_sql_injection(string: str) -> bool:
    if re.findall(r"(and|or|union|where|limit|group by|select)", string.lower()):
        raise SQLInjectionError(string)


async def check_password(password: str) -> bool:
    await check_sql_injection(password)
    if re.findall(r"[A-Za-z\d\_]+", password):
        return True


async def check_username(username: str) -> str:
    # await check_sql_injection(username)

    # Check email
    if re.findall(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", username):
        return UsernameType.email

    # Check phone
    elif re.findall(r"\d{1}\d{3}\d{3}\d{4}", username):
        return UsernameType.phone

    # Check username
    elif re.findall(r"[A-Za-z\d\_]+", username):
        return UsernameType.regular


async def check_url(url: str) -> str:
    result = urlparse(url)
    if all([result.scheme, result.netloc, result.path]):
        return result.path.split("/")[-1]


async def check_name(name: str) -> bool:
    if re.findall(r"[A-Za-z|А-Яа-я]+", name):
        return True


async def check_email(email: str) -> str:
    if re.findall(r"\w+\@\w+\.\w+", email):
        return email


async def make_password(string: str) -> bytes:
    return bcrypt.hashpw(string.encode("utf-8"), bcrypt.gensalt(12))
