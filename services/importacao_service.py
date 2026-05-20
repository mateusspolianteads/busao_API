from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.cliente import Cliente
from models.pedido import Pedido
import pandas as pd
from io import BytesIO
from datetime import datetime

def processar_planilha_clientes_e_pedidos(
    db: Session, evento_id: int, conteudo_arquivo: bytes, nome_arquivo: str
) -> dict:
    if not (nome_arquivo.endswith(".xlsx") or nome_arquivo.endswith(".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido. Apenas .xlsx ou .xls são aceitos.",
        )

    try:
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
        raise HTTPException(status_code=400, detail="Erro ao ler o arquivo Excel.")

    clientes_importados = []
    pedidos_importados = 0

    cpf_para_id_map = {c[0]: c[1] for c in db.query(Cliente.cpf, Cliente.id).all()}
    pedidos_no_banco = {p_id[0] for p_id in db.query(Pedido.id).all()}

    print(f"DEBUG: Iniciando processamento de {len(df)} linhas.")

    try:
        for index, row in df.iterrows():
            # Log de progresso a cada 10 linhas
            if index % 10 == 0: print(f"DEBUG: Processando linha {index}...")

            raw_cpf = row.get("cpf")
            if pd.isna(raw_cpf): continue
                
            # Tratamento CPF
            if isinstance(raw_cpf, (float, int)):
                cpf = str(int(raw_cpf)).strip()
            else:
                cpf = str(raw_cpf).strip().replace(".0", "")

            cliente_id = None

            # --- PASSO 1: CLIENTE ---
            if cpf in cpf_para_id_map:
                cliente_id = cpf_para_id_map[cpf]
            else:
                try:
                    novo_cliente = Cliente(
                        nome=str(row["nome"]).strip(),
                        cpf=cpf,
                        email=str(row.get("email", "")).strip(),
                        telefone=str(row.get("telefone_do_comprador", row.get("telefone", ""))).strip(),
                        data_nascimento=(pd.to_datetime(row.get("data_de_nascimento", row.get("data_nascimento"))).date() 
                                         if pd.notna(row.get("data_de_nascimento", row.get("data_nascimento"))) else None)
                    )
                    db.add(novo_cliente)
                    db.flush()
                    cliente_id = novo_cliente.id
                    cpf_para_id_map[cpf] = cliente_id
                    clientes_importados.append({"nome": novo_cliente.nome, "cpf": novo_cliente.cpf})
                except Exception as e:
                    print(f"ERRO NA LINHA {index} (Cliente): {e}")
                    continue

            # --- PASSO 2: PEDIDO ---
            id_pedido_bruto = row.get("id_do_pedido", row.get("id"))
            if pd.isna(id_pedido_bruto): continue
            id_pedido = int(float(id_pedido_bruto))

            if id_pedido in pedidos_no_banco: continue

            try:
                data_venda_bruta = row.get("data_de_venda", row.get("data_venda"))
                novo_pedido = Pedido(
                    id=id_pedido,
                    cliente_id=cliente_id,
                    evento_id=evento_id,
                    data_venda=pd.to_datetime(data_venda_bruta).to_pydatetime() if pd.notna(data_venda_bruta) else datetime.now(),
                    status_pedido=str(row.get("status_do_pedido", "Aprovado")).strip(),
                    status_ingresso=str(row.get("status_do_ingresso", "Válido")).strip(),
                    lote=str(row.get("lote", "1º Lote")).strip(),
                    valor_lote=float(row.get("valor_do_lote", row.get("valor", 0.0))),
                    canal_venda=str(row.get("canal_de_venda", "Online")).strip(),
                    metodo_pagamento=str(row.get("metodo_pagamento", "Pix")).strip(),
                    transferido=str(row.get("transferido")).strip() if pd.notna(row.get("transferido")) else None,
                    aprovado=str(row.get("aprovado", "Sim")).strip(),
                )
                db.add(novo_pedido)
                pedidos_no_banco.add(id_pedido)
                pedidos_importados += 1
            except Exception as e:
                print(f"ERRO NA LINHA {index} (Pedido): {e}")
                continue

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