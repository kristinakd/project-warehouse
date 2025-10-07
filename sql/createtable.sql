-- Создание таблиц

-- таблица-справочник "Пол"
CREATE TABLE gender (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code CHAR(1) UNIQUE NOT NULL, -- 'ж', 'м', 'у'
    name VARCHAR(50) NOT NULL     -- 'женский', 'мужской', 'унисекс'
);

-- таблица-справочник "Тип (одежда, обувь)"
CREATE TABLE product_type (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code CHAR(3) UNIQUE NOT NULL, -- 'CL', 'SH'
    name VARCHAR(50) NOT NULL     -- 'одежда', 'обувь'
);

-- таблица-справочник "Подтип (футболка, брюки, шорты, кеды)"
CREATE TABLE product_subtype (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code CHAR(3) UNIQUE NOT NULL, -- 'TSH', 'TRO', 'SHO', 'SNK'
    name VARCHAR(50) NOT NULL,    -- 'T-shirt', 'trousers', 'shorts', 'sneakers'
    product_type_id UUID NOT NULL REFERENCES product_type(id)
);

-- таблица-справочник "Цвет"
CREATE TABLE color (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code CHAR(3) UNIQUE NOT NULL, -- 'RED', 'BLU', 'GRN'
    name VARCHAR(50) NOT NULL     -- 'красный', 'синий', 'зеленый'
);

-- таблица-справочник "Размер"
CREATE TABLE clothing_size (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(5) UNIQUE NOT NULL -- 'XS', 'S', 'M', 'L', 'XL', '36'...'44'
);

-- таблица связка подтип + пол + размер
CREATE TABLE subtype_size_gender (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_subtype_id UUID NOT NULL REFERENCES product_subtype(id),
    gender_id UUID NOT NULL REFERENCES gender(id),
    clothing_size_id UUID NOT NULL REFERENCES clothing_size(id)
);

-- таблица "Товары"
CREATE TABLE product (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku CHAR(8) UNIQUE NOT NULL,    -- артикул
    name VARCHAR(50),      -- название товара
    price NUMERIC(12, 2) NOT NULL,  -- стоимость
    quantity INT NOT NULL,             -- количество
    subtype_size_gender_id UUID NOT NULL REFERENCES subtype_size_gender(id),
    color_id UUID NOT NULL REFERENCES color(id)
);
