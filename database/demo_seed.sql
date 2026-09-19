-- Dados fictícios e opcionais. Não cria vendas, clientes nem operações de caixa.
-- Selecione antes o banco de desenvolvimento correto no Workbench.
INSERT INTO products (name, normalized_name, price, category_id)
SELECT 'Coca-Cola', 'coca-cola', 7.50, category_id FROM categories
WHERE name = 'Bebidas' AND NOT EXISTS (
    SELECT 1 FROM products WHERE normalized_name = 'coca-cola'
);
INSERT INTO products (name, normalized_name, price, category_id)
SELECT 'X-Salada', 'x-salada', 22.90, category_id FROM categories
WHERE name = 'Lanches' AND NOT EXISTS (
    SELECT 1 FROM products WHERE normalized_name = 'x-salada'
);
INSERT INTO products (name, normalized_name, price, category_id)
SELECT 'Pudim', 'pudim', 9.00, category_id FROM categories
WHERE name = 'Sobremesas' AND NOT EXISTS (
    SELECT 1 FROM products WHERE normalized_name = 'pudim'
);
