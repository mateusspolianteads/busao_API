## Relatório de Performance e Sugestões de Indexação

Baseado nas consultas detectadas no código, segue uma lista de índices sugeridos para melhorar performance.

- Usuários:
  - `CREATE INDEX idx_usuarios_email ON usuarios (email);`
  - `CREATE INDEX idx_usuarios_cpf_cnpj ON usuarios (cpf_cnpj);`

- Clientes:
  - `CREATE INDEX idx_clientes_cpf ON clientes (cpf);`
  - `CREATE INDEX idx_clientes_email ON clientes (email);`

- Pedidos:
  - `CREATE INDEX idx_pedidos_evento_id ON pedidos (evento_id);`
  - `CREATE INDEX idx_pedidos_cliente_id ON pedidos (cliente_id);`
  - `CREATE INDEX idx_pedidos_data_venda ON pedidos (data_venda);`
  - `CREATE INDEX idx_pedidos_canal_venda ON pedidos (canal_venda);`

- Eventos:
  - `CREATE INDEX idx_eventos_categoria_id ON eventos (categoria_id);`

Observações:
- Analise o plano de execução (`EXPLAIN ANALYZE`) antes de aplicar índices em produção.
- Evite criar índices redundantes ou pouco utilizados — eles impactam gravações.
- Se a base for muito grande, considere índices parciais para consultas frequentes (e.g., WHERE evento_id = X).
