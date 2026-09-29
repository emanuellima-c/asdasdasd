from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

# ==================== PRODUTOS ====================
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    preco: float = Field(..., gt=0)
    quantidade: int = Field(0, ge=0)

    @validator('preco')
    def preco_nao_pode_ser_zero(cls, v):
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v

    @validator('nome')
    def nome_nao_pode_ser_vazio(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Nome não pode ser vazio')
        return v.strip()

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    preco: Optional[float] = Field(None, gt=0)
    quantidade: Optional[int] = Field(None, ge=0)

    @validator('preco')
    def preco_nao_pode_ser_zero(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        return v

    @validator('nome')
    def nome_nao_pode_ser_vazio(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError('Nome não pode ser vazio')
        return v

class ProdutoResponse(ProdutoBase):
    id: int
    data_cadastro: datetime

    class Config:
        orm_mode = True

# ==================== USUÁRIOS E AUTENTICAÇÃO ====================
class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    senha: str = Field(..., min_length=6)
    nome_completo: Optional[str] = None

class UsuarioResponse(BaseModel):
    id: int
    username: str
    nome_completo: Optional[str]
    ativo: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
