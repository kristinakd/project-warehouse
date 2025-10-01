-- Наполнение таблиц

-- таблица-справочник "Пол"
INSERT INTO gender (code, name) VALUES
('ж', 'женский'),
('м', 'мужской'),
('у', 'унисекс');


-- таблица-справочник "Тип (одежда, обувь)"
INSERT INTO product_type (code, name) VALUES
('CL', 'одежда'),
('SH', 'обувь');

-- таблица-справочник "Подтип (футболка, брюки, шорты, кеды)"
INSERT INTO product_subtype (code, name, product_type_id) VALUES
('TSH', 'T-shirt', (SELECT id FROM product_type WHERE code='CL')),
('TRO', 'trousers', (SELECT id FROM product_type WHERE code='CL')),
('SHO', 'shorts', (SELECT id FROM product_type WHERE code='CL')),
('SNK', 'sneakers', (SELECT id FROM product_type WHERE code='SH'));


-- таблица-справочник "Цвет"
INSERT INTO product_type (code, name) VALUES
('RED', 'красный'),
('BLU', 'синий'),
('GRN', 'зеленый');

-- таблица-справочник "Размер"
INSERT INTO clothing_size (code) VALUES
('XS'),
('S'),
('M'),
('L'),
('XL'),
('36'),
('37'),
('38'),
('39'),
('40'),
('41'),
('42'),
('43'),
('44');

