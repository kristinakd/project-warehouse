# project-warehouse
Учебный проект — управление складом товаров для бренда X

## О себе
Системный аналитик в банке

## О проекте 
Простой REST API (Warehouse API) для управления товарами на складе.

## 🔹 Основные возможности Warehouse API
- Добавление товара (`POST /product`)
- Обновление количества товара (`PATCH /product/<sku>`)
- Удаление товара (`DELETE /product/<sku>`)
- Поиск товаров по фильтрам (`POST /products/search`)

## 🔹 Стек технологий

- Python 3.9
- Flask
- PostgreSQL
