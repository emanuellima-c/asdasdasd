from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class Produto(Base):
    """Modelo de Produto"""
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    preco = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False, default=0)
    data_cadastro = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Produto {self.nome} - R${self.preco}>"

class Usuario(Base):
    """Modelo de Usuário para autenticação"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nome_completo = Column(String(100), nullable=True)
    ativo = Column(Integer, default=1)  # 1 = ativo, 0 = inativo
