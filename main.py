from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import models
import schemas
from database import SessionLocal, engine
from auth import (
    get_db, autenticar_usuario, criar_token_acesso,
    get_current_user, gerar_hash_senha, ACCESS_TOKEN_EXPIRE_MINUTES
)

# Criar as tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API da Mercearia do João",
    description="API com autenticação JWT + Frontend",
    version="3.0.0"
)

# Permitir que o frontend se comunique com a API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção coloque só o domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== AUTENTICAÇÃO ====================

@app.post("/registrar", response_model=schemas.UsuarioResponse, status_code=201)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastrar um novo usuário"""
    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.username == usuario.username
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Nome de usuário já existe")

    novo_usuario = models.Usuario(
        username=usuario.username,
        senha_hash=gerar_hash_senha(usuario.senha),
        nome_completo=usuario.nome_completo
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Fazer login e receber o token JWT"""
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": usuario.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/eu", response_model=schemas.UsuarioResponse)
def ler_usuario_atual(usuario_atual: models.Usuario = Depends(get_current_user)):
    """Retorna os dados do usuário logado"""
    return usuario_atual

# ==================== PRODUTOS (protegidos) ====================

@app.get("/")
def home():
    return {
        "mensagem": "API da Mercearia do João com Autenticação 🔐",
        "docs": "/docs",
        "frontend": "Abra o arquivo frontend/index.html no navegador"
    }

@app.post("/produtos", response_model=schemas.ProdutoResponse, status_code=201)
def criar_produto(
    produto: schemas.ProdutoCreate,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_current_user)
):
    """Criar produto (precisa estar logado)"""
    db_produto = models.Produto(
        nome=produto.nome,
        preco=produto.preco,
        quantidade=produto.quantidade
    )
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.get("/produtos", response_model=List[schemas.ProdutoResponse])
def listar_produtos(
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_current_user)
):
    """Listar produtos (precisa estar logado)"""
    return db.query(models.Produto).all()

@app.get("/produtos/{produto_id}", response_model=schemas.ProdutoResponse)
def buscar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_current_user)
):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.put("/produtos/{produto_id}", response_model=schemas.ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    produto_update: schemas.ProdutoUpdate,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_current_user)
):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    update_data = produto_update.dict(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto

@app.delete("/produtos/{produto_id}")
def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_current_user)
):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    nome = produto.nome
    db.delete(produto)
    db.commit()
    return {"mensagem": f"Produto '{nome}' removido com sucesso"}

@app.put("/produtos/{produto_id}/aumentar/{quantidade}")
def aumentar_estoque(
    produto_id: int,
    quantidade: int,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_current_user)
):
    if quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser positiva")

    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.quantidade += quantidade
    db.commit()
    db.refresh(produto)
    return {
        "mensagem": f"Estoque aumentado em {quantidade} unidades",
        "produto": produto.nome,
        "estoque_atual": produto.quantidade
    }
