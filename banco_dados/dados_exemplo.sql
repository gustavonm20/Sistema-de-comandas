-- Dados fictícios e opcionais. Não cria vendas, clientes nem operações de caixa.
-- Selecione antes o banco de desenvolvimento correto no Workbench.
INSERT INTO produtos (nome, nome_normalizado, preco, id_categoria)
SELECT 'Coca-Cola', 'coca-cola', 7.50, id_categoria FROM categorias
WHERE nome = 'Bebidas' AND NOT EXISTS (
    SELECT 1 FROM produtos WHERE nome_normalizado = 'coca-cola'
);
INSERT INTO produtos (nome, nome_normalizado, preco, id_categoria)
SELECT 'X-Salada', 'x-salada', 22.90, id_categoria FROM categorias
WHERE nome = 'Lanches' AND NOT EXISTS (
    SELECT 1 FROM produtos WHERE nome_normalizado = 'x-salada'
);
INSERT INTO produtos (nome, nome_normalizado, preco, id_categoria)
SELECT 'Pudim', 'pudim', 9.00, id_categoria FROM categorias
WHERE nome = 'Sobremesas' AND NOT EXISTS (
    SELECT 1 FROM produtos WHERE nome_normalizado = 'pudim'
);
