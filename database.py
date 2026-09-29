
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão (usando SQLite - banco simples em arquivo)
# SQLite é perfeito para começar porque não precisa instalar nada!
DATABASE_URL = "sqlite:///./mercearia.db"

# Criando o "motor" do banco
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Criando a "fábrica de sessões"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para criar as tabelas
Base = declarative_base()

    