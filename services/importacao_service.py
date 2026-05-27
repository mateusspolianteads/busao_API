import asyncio
import pandas as pd
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from models.cliente import Cliente
from models.pedido import Pedido

async def processar_planilha_clientes_e_pedidos(
    request: Request, db: Session, evento_id: int, conteudo_arquivo: bytes, nome_arquivo: str
) -> dict:
    if not (nome_arquivo.endswith(".xlsx") or nome_arquivo.endswith(".xls") or nome_arquivo.endswith(".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido. Apenas .xlsx, .xls ou .csv são aceitos.",
        )

    try:
        if nome_arquivo.endswith(".csv"):
            df = pd.read_csv(BytesIO(conteudo_arquivo))
        else:
            df = pd.read_excel(BytesIO(conteudo_arquivo))
            
        df.columns = (
            df.columns.str.normalize('NFKD')
            .str.encode('ascii', errors='ignore')
            .str.decode('utf-8')
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
    except Exception as e:
        print(f"ERRO AO LER PLANILHA: {e}")
        raise HTTPException(status_code=400, detail="Erro ao ler o arquivo.")

    clientes_importados = []
    pedidos_importados = 0

    # 1. Mapeamento de Clientes existentes
    cpf_para_id_map = {c[0]: c[1] for c in db.query(Cliente.cpf, Cliente.id).all()}

    # Função auxiliar para garantir formato estrito de data texturizada (AAAA-MM-DD HH:MM:SS)
    def formatar_data_estrita(dt):
        if dt is None or pd.isna(dt):
            return None
        if isinstance(dt, str):
            dt = pd.to_datetime(dt, errors='coerce')
        if hasattr(dt, "to_pydatetime"):
            dt = dt.to_pydatetime()
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return str(dt)

    # 2. Carregar pedidos já existentes NO BANCO (Filtrando APENAS para o evento atual por performance)
    pedidos_no_banco = set()
    pedidos_existentes_query = db.query(
        Pedido.cliente_id,
        Pedido.evento_id,
        Pedido.data_venda,
        Pedido.valor_lote,
        Pedido.canal_venda,
        Pedido.metodo_pagamento,
    ).filter(Pedido.evento_id == evento_id).all()

    for cliente_id_db, evento_id_db, data_venda_db, valor_lote_db, canal_venda_db, metodo_pagamento_db in pedidos_existentes_query:
        pedidos_no_banco.add(
            (
                cliente_id_db,
                evento_id_db,
                formatar_data_estrita(data_venda_db),
                round(float(valor_lote_db), 2) if valor_lote_db is not None else 0.0,
                str(canal_venda_db).strip().lower() if canal_venda_db else None,
                str(metodo_pagamento_db).strip().lower() if metodo_pagamento_db else None,
            )
        )

    # Identificação Dinâmica de Colunas
    col_telefone = "telefone_do_comprador" if "telefone_do_comprador" in df.columns else "telefone"
    col_nasc = "data_de_nascimento" if "data_de_nascimento" in df.columns else "data_nascimento"
    col_data_venda = "data_de_venda" if "data_de_venda" in df.columns else "data_venda"
    col_status_pedido = "status_do_pedido" if "status_do_pedido" in df.columns else "status_pedido"
    col_status_ingresso = "status_do_ingresso" if "status_do_ingresso" in df.columns else "status_ingresso"
    col_valor_lote = "valor_do_lote" if "valor_do_lote" in df.columns else "valor"
    col_canal_venda = "canal_de_venda" if "canal_de_venda" in df.columns else "canal_venda"
    col_metodo_pagamento = "metodo_de_pagamento" if "metodo_de_pagamento" in df.columns else "metodo_pagamento"

    col_id_pedido = None
    if "id_pedido" in df.columns:
        col_id_pedido = "id_pedido"
    elif "pedido_id" in df.columns:
        col_id_pedido = "pedido_id"
    elif "id" in df.columns:
        col_id_pedido = "id"

    def limpar_cpf(raw_cpf):
        if pd.isna(raw_cpf):
            return None
        if isinstance(raw_cpf, (float, int)):
            return str(int(raw_cpf)).strip()
        return str(raw_cpf).strip().replace(".0", "")

    def limpar_id_pedido(raw):
        if pd.isna(raw):
            return None
        if isinstance(raw, (float, int)):
            return int(raw)
        raw_str = str(raw).strip()
        return int(raw_str) if raw_str.isdigit() else None

    # Limpeza inicial do DataFrame
    df["_cpf_limpo"] = df["cpf"].apply(limpar_cpf) if "cpf" in df.columns else None
    df["_data_nasc_limpa"] = pd.to_datetime(df[col_nasc], errors='coerce').dt.date if col_nasc in df.columns else None
    df["_data_venda_limpa"] = pd.to_datetime(df[col_data_venda], errors='coerce') if col_data_venda in df.columns else None
    df["_id_pedido_limpo"] = df[col_id_pedido].apply(limpar_id_pedido) if col_id_pedido in df.columns else None

    print(f"DEBUG: Iniciando processamento de {len(df)} linhas.")

    # 3. Processamento e inserção em lote de novos clientes
    df_validos = df[df["_cpf_limpo"].notna()]
    cpfs_unicos = df_validos["_cpf_limpo"].unique()
    cpfs_novos = [cpf for cpf in cpfs_unicos if cpf not in cpf_para_id_map]

    if cpfs_novos:
        df_novos_clientes = df_validos[df_validos["_cpf_limpo"].isin(cpfs_novos)].drop_duplicates(subset=["_cpf_limpo"])
        novos_clientes_objs = []
        
        for _, row in df_novos_clientes.iterrows():
            nome_val = row.get("nome")
            email_val = row.get("email")
            telefone_val = row.get(col_telefone) if col_telefone in df.columns else None
            
            novo_cliente = Cliente(
                nome=str(nome_val).strip() if pd.notna(nome_val) else None,
                cpf=row["_cpf_limpo"],
                email=str(email_val).strip() if pd.notna(email_val) else None,
                telefone=str(telefone_val).strip() if pd.notna(telefone_val) else None,
                data_nascimento=row["_data_nasc_limpa"] if pd.notna(row["_data_nasc_limpa"]) else None
            )
            novos_clientes_objs.append(novo_cliente)
            
        try:
            db.add_all(novos_clientes_objs)
            db.flush()
            
            for c in novos_clientes_objs:
                cpf_para_id_map[c.cpf] = c.id
                clientes_importados.append({"nome": c.nome, "cpf": c.cpf})
        except Exception as e:
            db.rollback()
            print(f"ERRO AO SALVAR LOTE DE CLIENTES: {e}")
            raise HTTPException(status_code=400, detail=f"Erro ao salvar lote de novos clientes: {str(e)}")

    linhas_planilha = df.to_dict(orient="records")

    # 4. Processamento Iterativo de Pedidos
    try:
        for index, row in enumerate(linhas_planilha):
            if index % 50 == 0: 
                print(f"DEBUG: Processando linha {index}...")
                if await request.is_disconnected():
                    print(f"❌ [CANCELADO] O usuário cancelou a importação no front-end na linha {index}!")
                    db.rollback()
                    return {
                        "status": "cancelado",
                        "message": f"Importação interrompida pelo usuário na linha {index}.",
                        "total_clientes_novos": len(clientes_importados),
                        "total_pedidos_criados": pedidos_importados
                    }
                await asyncio.sleep(0)

            cpf = row.get("_cpf_limpo")
            if not cpf:
                continue

            cliente_id = cpf_para_id_map.get(cpf)
            if not cliente_id:
                continue

            id_pedido = row.get("_id_pedido_limpo")
            if id_pedido == -1:
                continue

            # Valores da linha atual para validação estrita
            data_venda_val = row.get("_data_venda_limpa")
            valor_lote_val = row.get(col_valor_lote) if col_valor_lote in row else None
            canal_venda_val = row.get(col_canal_venda) if col_canal_venda in row else None
            metodo_pagamento_val = row.get(col_metodo_pagamento) if col_metodo_pagamento in row else None

            # Montagem Normalizada da Chave de Comparação (Igual ao que fizemos acima para o banco)
            data_venda_key = formatar_data_estrita(data_venda_val)
            valor_lote_key = round(float(valor_lote_val), 2) if pd.notna(valor_lote_val) else 0.0
            canal_venda_key = str(canal_venda_val).strip().lower() if pd.notna(canal_venda_val) else None
            metodo_pagamento_key = str(metodo_pagamento_val).strip().lower() if pd.notna(metodo_pagamento_val) else None

            pedido_chave = (
                cliente_id,
                evento_id,
                data_venda_key,
                valor_lote_key,
                canal_venda_key,
                metodo_pagamento_key,
            )

            # Se a chave exata já existe no set (Banco ou inserido na mesma execução), ignora
            if pedido_chave in pedidos_no_banco:
                continue

            try:
                status_pedido_val = row.get(col_status_pedido) if col_status_pedido in row else None
                status_ingresso_val = row.get(col_status_ingresso) if col_status_ingresso in row else None
                lote_val = row.get("lote")
                transferido_val = row.get("transferido")
                aprovado_val = row.get("aprovado")
                if pd.isna(aprovado_val):
                    aprovado_val = "--"

                novo_pedido = Pedido(
                    cliente_id=cliente_id,
                    evento_id=evento_id,
                    data_venda=data_venda_val.to_pydatetime() if pd.notna(data_venda_val) else datetime.now(),
                    status_pedido=str(status_pedido_val).strip() if pd.notna(status_pedido_val) else None,
                    status_ingresso=str(status_ingresso_val).strip() if pd.notna(status_ingresso_val) else None,
                    lote=str(lote_val).strip() if pd.notna(lote_val) else None,
                    valor_lote=valor_lote_val if pd.notna(valor_lote_val) else 0.0,
                    canal_venda=str(canal_venda_val).strip() if pd.notna(canal_venda_val) else None,
                    metodo_pagamento=str(metodo_pagamento_val).strip() if pd.notna(metodo_pagamento_val) else None,
                    transferido=str(transferido_val).strip() if pd.notna(transferido_val) else None,
                    aprovado=str(aprovado_val).strip()
                )
                db.add(novo_pedido)
                
                # Adiciona no set dinamicamente para evitar duplicados repetidos na própria planilha
                pedidos_no_banco.add(pedido_chave)
                pedidos_importados += 1
            except Exception as e:
                db.rollback()
                print(f"ERRO CRÍTICO NA LINHA {index} (Pedido): {e}")
                raise HTTPException(status_code=400, detail=f"Erro na linha {index} ao salvar pedido: {str(e)}")

        db.commit()
        print("DEBUG: Processamento concluído com sucesso.")
        return {
            "total_clientes_novos": len(clientes_importados),
            "total_pedidos_criados": pedidos_importados,
            "clientes_importados": clientes_importados,
        }

    except Exception as e:
        db.rollback()
        print(f"ERRO CRÍTICO NO COMMIT: {e}")
        raise HTTPException(status_code=500, detail=f"Erro fatal: {str(e)}")