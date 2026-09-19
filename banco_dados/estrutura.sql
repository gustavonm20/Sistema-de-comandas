-- Inicialização de banco NOVO. Não é uma migração. Consulte documentacao/BANCO_DADOS.md.
CREATE DATABASE IF NOT EXISTS comandas
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE comandas;

CREATE TABLE IF NOT EXISTS estabelecimentos (
    id_estabelecimento INT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    correio VARCHAR(150) NOT NULL,
    tipo_estabelecimento VARCHAR(100) NOT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE (nome)
);

CREATE TABLE IF NOT EXISTS produtos (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    nome_normalizado VARCHAR(100) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    id_categoria INT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX indice_produtos_categoria_ativo (id_categoria, ativo),
    UNIQUE (nome_normalizado),
    CHECK (preco >= 0),
    FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
);

CREATE TABLE IF NOT EXISTS cartoes_comanda (
    id_cartao INT AUTO_INCREMENT PRIMARY KEY,
    numero_cartao CHAR(4) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE (numero_cartao),
    CHECK (numero_cartao REGEXP '^[0-9]{4}$')
);

CREATE TABLE IF NOT EXISTS operacoes_diarias (
    id_operacao INT AUTO_INCREMENT PRIMARY KEY,
    situacao ENUM('aberto', 'fechado') NOT NULL DEFAULT 'aberto',
    caixa_inicial DECIMAL(10, 2) NOT NULL,
    caixa_esperado DECIMAL(10, 2) NULL,
    caixa_contado DECIMAL(10, 2) NULL,
    valor_diferenca DECIMAL(10, 2) NULL,
    justificativa_diferenca VARCHAR(255) NULL,
    aberto_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fechado_em DATETIME NULL,

    marcador_operacao_aberta TINYINT
        GENERATED ALWAYS AS (
            CASE
                WHEN situacao = 'aberto' THEN 1
                ELSE NULL
            END
        ) STORED,

    UNIQUE (marcador_operacao_aberta),
    CHECK (caixa_inicial >= 0),
    CHECK (
        (situacao = 'aberto' AND fechado_em IS NULL)
        OR
        (situacao = 'fechado' AND fechado_em IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cartao INT NOT NULL,
    id_operacao INT NOT NULL,
    tipo_atendimento ENUM('mesa', 'balcao', 'retirada') NOT NULL DEFAULT 'balcao',
    identificacao_atendimento VARCHAR(100) NULL,
    observacao VARCHAR(255) NULL,
    situacao ENUM('aberto', 'fechado') NOT NULL DEFAULT 'aberto',
    aberto_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fechado_em DATETIME NULL,

    id_cartao_aberto INT
        GENERATED ALWAYS AS (
            CASE
                WHEN situacao = 'aberto' THEN id_cartao
                ELSE NULL
            END
        ) STORED,

    INDEX indice_pedidos_situacao_abertura (situacao, aberto_em),
    UNIQUE (id_cartao_aberto),
    FOREIGN KEY (id_cartao)
        REFERENCES cartoes_comanda(id_cartao),
    FOREIGN KEY (id_operacao)
        REFERENCES operacoes_diarias(id_operacao),
    CHECK (
        (situacao = 'aberto' AND fechado_em IS NULL)
        OR
        (situacao = 'fechado' AND fechado_em IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id_item_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_produto INT NOT NULL,
    observacoes VARCHAR(255) NULL,
    nome_produto_historico VARCHAR(100) NOT NULL,
    nome_categoria_historico VARCHAR(100) NOT NULL,
    preco_unitario DECIMAL(10, 2) NOT NULL,
    quantidade INT NOT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE (id_pedido, id_produto),
    CHECK (preco_unitario >= 0),
    CHECK (quantidade > 0),
    FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_produto)
        REFERENCES produtos(id_produto)
);

CREATE TABLE IF NOT EXISTS vendas (
    id_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    numero_cartao_historico CHAR(4) NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL,
    forma_pagamento ENUM('dinheiro', 'pix', 'debito', 'credito') NOT NULL,
    valor_recebido DECIMAL(10, 2) NULL,
    troco DECIMAL(10, 2) NULL,
    vendido_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX indice_vendas_data (vendido_em),
    INDEX indice_vendas_pagamento_data (forma_pagamento, vendido_em),
    UNIQUE (id_pedido),
    CHECK (valor_total >= 0),
    FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido)
);

CREATE TABLE IF NOT EXISTS registros_auditoria (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    responsavel VARCHAR(100) NOT NULL,
    acao VARCHAR(100) NOT NULL,
    tipo_entidade VARCHAR(50) NOT NULL,
    id_entidade INT NULL,
    detalhe VARCHAR(255) NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO estabelecimentos (id_estabelecimento, nome, correio, tipo_estabelecimento)
SELECT 1, 'Meu Estabelecimento', 'contato@estabelecimento.com', 'Padaria e cafeteria'
WHERE NOT EXISTS (
    SELECT 1
    FROM estabelecimentos
    WHERE id_estabelecimento = 1
);

INSERT INTO categorias (nome)
SELECT 'Bebidas'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nome = 'Bebidas');

INSERT INTO categorias (nome)
SELECT 'Frios'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nome = 'Frios');

INSERT INTO categorias (nome)
SELECT 'Lanches'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nome = 'Lanches');

INSERT INTO categorias (nome)
SELECT 'Pizzas'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nome = 'Pizzas');

INSERT INTO categorias (nome)
SELECT 'Sobremesas'
WHERE NOT EXISTS (SELECT 1 FROM categorias WHERE nome = 'Sobremesas');

INSERT IGNORE INTO cartoes_comanda (numero_cartao) VALUES
    ('0001'), ('0002'), ('0003'), ('0004'), ('0005'),
    ('0006'), ('0007'), ('0008'), ('0009'), ('0010'),
    ('0011'), ('0012'), ('0013'), ('0014'), ('0015'),
    ('0016'), ('0017'), ('0018'), ('0019'), ('0020');

CREATE OR REPLACE VIEW visao_produtos AS
SELECT
    p.id_produto,
    p.nome AS nome_produto,
    p.preco,
    c.id_categoria,
    c.nome AS nome_categoria,
    p.ativo
FROM produtos p
JOIN categorias c
    ON p.id_categoria = c.id_categoria;


CREATE OR REPLACE VIEW visao_pedidos_abertos AS
SELECT
    o.id_pedido,
    cc.numero_cartao,
    o.situacao,

    DATE_FORMAT(
        o.aberto_em,
        '%H:%i  %d/%m/%Y'
    ) AS aberto_em,

    COALESCE(
        SUM(oi.quantidade * oi.preco_unitario),
        0
    ) AS valor_total

FROM pedidos o

JOIN cartoes_comanda cc
    ON o.id_cartao = cc.id_cartao

LEFT JOIN itens_pedido oi
    ON o.id_pedido = oi.id_pedido

WHERE o.situacao = 'aberto'

GROUP BY
    o.id_pedido,
    cc.numero_cartao,
    o.situacao,
    o.aberto_em;


CREATE OR REPLACE VIEW visao_resumo_pedidos AS
SELECT
    o.id_pedido,
    cc.numero_cartao,
    o.situacao,

    DATE_FORMAT(
        o.aberto_em,
        '%H:%i  %d/%m/%Y'
    ) AS aberto_em,

    DATE_FORMAT(
        o.fechado_em,
        '%H:%i  %d/%m/%Y'
    ) AS fechado_em,

    p.id_produto,
    oi.nome_produto_historico AS nome_produto,
    oi.nome_categoria_historico AS nome_categoria,

    oi.quantidade,
    oi.preco_unitario,

    oi.quantidade * oi.preco_unitario AS subtotal,

    oi.observacoes,

    SUM(
        oi.quantidade * oi.preco_unitario
    ) OVER (
        PARTITION BY o.id_pedido
    ) AS total_pedido

FROM pedidos o

JOIN cartoes_comanda cc
    ON o.id_cartao = cc.id_cartao

JOIN itens_pedido oi
    ON o.id_pedido = oi.id_pedido

JOIN produtos p
    ON oi.id_produto = p.id_produto

JOIN categorias c
    ON p.id_categoria = c.id_categoria;


CREATE OR REPLACE VIEW visao_historico_vendas AS
SELECT
    s.id_venda,
    s.id_pedido,
    s.numero_cartao_historico AS numero_cartao,
    s.valor_total,
    s.forma_pagamento,

    CASE s.forma_pagamento
        WHEN 'dinheiro' THEN 'Dinheiro'
        WHEN 'credito' THEN 'Crédito'
        WHEN 'debito' THEN 'Débito'
        WHEN 'pix' THEN 'PIX'
    END AS rotulo_forma_pagamento,

    DATE_FORMAT(
        s.vendido_em,
        '%H:%i  %d/%m/%Y'
    ) AS vendido_em,

    s.vendido_em AS data_venda_original

FROM vendas s

JOIN pedidos o
    ON s.id_pedido = o.id_pedido

JOIN cartoes_comanda cc
    ON o.id_cartao = cc.id_cartao;


CREATE OR REPLACE VIEW visao_resumo_diario AS
SELECT
    data_resumo,
    DATE_FORMAT(data_resumo, '%d/%m/%Y') AS rotulo_data,
    total_vendas,
    faturamento_total,
    valor_medio_venda
FROM (
    SELECT DATE(vendido_em) AS data_resumo,
           COUNT(*) AS total_vendas,
           SUM(valor_total) AS faturamento_total,
           AVG(valor_total) AS valor_medio_venda
    FROM vendas
    GROUP BY DATE(vendido_em)
) AS vendas_diarias;


CREATE OR REPLACE VIEW visao_resumo_semanal AS
SELECT
    YEARWEEK(vendido_em, 1) AS ano_semana,

    MIN(DATE(vendido_em)) AS data_primeira_venda,

    MAX(DATE(vendido_em)) AS data_ultima_venda,

    COUNT(*) AS total_vendas,

    SUM(valor_total) AS faturamento_total,

    AVG(valor_total) AS valor_medio_venda

FROM vendas

GROUP BY YEARWEEK(vendido_em, 1);


CREATE OR REPLACE VIEW visao_resumo_mensal AS
SELECT
    YEAR(vendido_em) AS ano,
    MONTH(vendido_em) AS mes,

    DATE_FORMAT(
        vendido_em,
        '%m/%Y'
    ) AS rotulo_mes,

    COUNT(*) AS total_vendas,

    SUM(valor_total) AS faturamento_total,

    AVG(valor_total) AS valor_medio_venda

FROM vendas

GROUP BY
    YEAR(vendido_em),
    MONTH(vendido_em),
    DATE_FORMAT(vendido_em, '%m/%Y');
