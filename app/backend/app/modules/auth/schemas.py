from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=5, max_length=180)
    cpf: str = Field(min_length=11, max_length=14)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if len(value) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("E-mail invalido")
        return value

    @field_validator("cpf")
    @classmethod
    def normalize_cpf(cls, value: str) -> str:
        digits = only_digits(value)
        if not is_valid_cpf(digits):
            raise ValueError("CPF invalido")
        return digits


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserRead(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def is_valid_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    numbers = [int(digit) for digit in cpf]
    for digit_index in (9, 10):
        total = sum(numbers[index] * ((digit_index + 1) - index) for index in range(digit_index))
        check_digit = (total * 10) % 11
        if check_digit == 10:
            check_digit = 0
        if numbers[digit_index] != check_digit:
            return False
    return True
