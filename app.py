from flask import Flask, jsonify, request
import psycopg2
import random
import re

# Генератор артикула
def generate_sku(conn):
    while True:
        # Генерация артикула
        sku = ''.join(str(random.randint(0, 9)) for _ in range(8))

        # Проверка уникальности артикула
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM product WHERE sku = %s", (sku,))
            exists = cursor.fetchone()[0]

        # Если артикул свободен, возвращаем его
        if exists == 0:
            return sku

app = Flask(__name__)

# Подключение к базе данных
conn = psycopg2.connect(host="localhost", database="postgres")

@app.route('/')
def read_root():
    return {"message": "Welcome to Warehouse API!"}

@app.route("/product/<string:sku>", methods=["DELETE"])
def delete_product(sku):
    # Проверяем корректность артикула
    if not re.match(r"^\d{8}$", sku):
        return jsonify({"message": "Некорректный формат артикула"}), 400

    # Пробуем удалить товар из базы
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM product WHERE sku = %s RETURNING sku", (sku,))
        deleted_row = cursor.fetchone()

    if deleted_row:
        conn.commit()
        return jsonify({"message": "Товар удален"}), 200
    else:
        return jsonify({"message": "Артикул не найден"}), 404

@app.route("/product/<string:sku>", methods=["PATCH"])
def update_product_quantity(sku):
    # Проверяем корректность артикула
    if not re.match(r"^\d{8}$", sku):
        return jsonify({"message": "Некорректный формат артикула"}), 400

    # Получаем данные из запроса
    data = request.get_json()
    new_quantity = data.get("quantity")

    # Проверяем, что параметр запроса передан и имеет верное значение
    if new_quantity is None or not isinstance(new_quantity, int) or new_quantity < 0:
        return jsonify({"message": "Некорректное значение количества товара"}), 400

    # Проверяем, существует ли товар с таким артикулом
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product WHERE sku = %s", (sku,))
        exists = cursor.fetchone()[0]

    if exists == 0:
        return jsonify({"message": "Артикул не найден"}), 404

    # Обновляем количество товара
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE product SET quantity = %s WHERE sku = %s", (new_quantity, sku))
            conn.commit()
        return jsonify({"message": "Количество товара изменено"}), 200
    except Exception:
        return jsonify({"message": "Непредвиденная ошибка"}), 500

@app.route("/product", methods=["POST"])
def add_product():
    # Получаем данные из запроса
    data = request.get_json()
    gender = data.get("gender")
    product_subtype = data.get("productSubtype")
    color = data.get("color")
    size = data.get("size")
    price = data.get("price")
    quantity = data.get("quantity", 0)

    # Проверяем параметры запроса на корректность
    if (gender is None or not isinstance(gender, str) or gender not in ['ж', 'м', 'у']) \
        or (product_subtype is None or not isinstance(product_subtype, str) or product_subtype not in ['TSH', 'TRO', 'SHO', 'SNK']) \
        or (color is None or not isinstance(color, str) or color not in ['RED', 'BLU', 'GRN']) \
        or (size is None or not isinstance(size, str) or size not in ['XS', 'S', 'M', 'L', 'XL', '36', '37', '38', '39', '40', '41', '42', '43']) \
        or (price is None or not isinstance(price, float) or price < 0):
            return jsonify({"message": "Некорректный запрос"}), 400

    # Генерация уникального артикула
    sku = generate_sku(conn)

    # Получаем идентификаторы из справочников
    try:
        with conn.cursor() as cursor:
            # Идентификатор цвета
            cursor.execute("SELECT id FROM color WHERE code = %s", (color,))
            color_id = cursor.fetchone()[0]

            # Идентификатор подтипа
            cursor.execute("SELECT id FROM product_subtype WHERE code = %s", (product_subtype,))
            product_subtype_id = cursor.fetchone()[0]

            # Идентификатор пола
            cursor.execute("SELECT id FROM gender WHERE code = %s", (gender,))
            gender_id = cursor.fetchone()[0]

            # Идентификатор размера
            cursor.execute("SELECT id FROM clothing_size WHERE code = %s", (size,))
            clothing_size_id = cursor.fetchone()[0]

            # Определение типа изделия
            cursor.execute("SELECT product_type_id FROM product_subtype WHERE code = %s", (product_subtype,))
            product_type_id = cursor.fetchone()[0]

            # Определяем type_size_gender_id
            cursor.execute(
                "SELECT id FROM type_size_gender WHERE product_type_id = %s AND gender_id = %s AND clothing_size_id = %s",
                (product_type_id, gender_id, clothing_size_id))
            type_size_gender_id = cursor.fetchone()[0]

            # Добавление товара
            cursor.execute("""
                INSERT INTO product (sku, type_size_gender_id, color_id, product_subtype_id, price, quantity)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (sku, type_size_gender_id, color_id, product_subtype_id, price, quantity))
            conn.commit()
            return jsonify({"message": "Товар успешно добавлен", "sku": sku}), 200
    except Exception:
        return jsonify({"message": "Ошибка добавления товара"}), 500

@app.route("/products/search", methods=["POST"])
def search_product():
    # Получаем данные из запроса
    data = request.get_json()

    conditions = []
    values = []

    # Фильтры
    if "gender" in data:
        conditions.append("g.code = %s")
        values.append(data.get("gender"))

    if "productSubtype" in data:
        conditions.append("pst.code = %s")
        values.append(data.get("productSubtype"))

    if "color" in data:
        conditions.append("cl.code = %s")
        values.append(data.get("color"))

    if "size" in data:
        conditions.append("cs.code = %s")
        values.append(data.get("size"))

    if "sku" in data:
        conditions.append("p.sku = %s")
        values.append(data.get("sku"))

    if "productType" in data:
        conditions.append("pt.code = %s")
        values.append(data.get("productType"))

    if "price" in data:
        conditions.append("p.price = %s")
        values.append(data.get("price"))

    if "isAvailable" in data:
        if data.get("isAvailable"):
            conditions.append("p.quantity > 0")
        else:
            conditions.append("p.quantity = 0")

    # Должно быть хотя бы одно условие
    if not conditions:
        return jsonify({"message": "Некорректный запрос: отсутствуют атрибуты поиска"}), 400

    base_query = """
        SELECT 
            p.sku, p.price, g.code AS gender, 
            pst.code AS productSubtype, cl.code AS color, cs.code AS size, 
            pt.code AS productType, 
            CASE WHEN p.quantity > 0 THEN TRUE ELSE FALSE END AS isAvailable
        FROM product p
        INNER JOIN product_subtype pst ON p.product_subtype_id = pst.id
        INNER JOIN color cl ON p.color_id = cl.id
        INNER JOIN type_size_gender tsg ON p.type_size_gender_id = tsg.id
        INNER JOIN gender g ON tsg.gender_id = g.id
        INNER JOIN clothing_size cs ON tsg.clothing_size_id = cs.id
        INNER JOIN product_type pt ON tsg.product_type_id = pt.id
    """

    # Добавляем условия
    where_clause = "WHERE " + " AND ".join(conditions)
    final_query = base_query + " " + where_clause

    try:
        with conn.cursor() as cursor:
            cursor.execute(final_query, tuple(values))
            rows = cursor.fetchall()
    except Exception:
        conn.rollback()
        return jsonify({"message": "Ошибка поиска"}), 500

    # Если ничего не найдено → 404
    if not rows:
        return jsonify({"message": "Ничего не найдено"}), 404

    # Формируем JSON по схеме SearchProduct
    result = []
    for row in rows:
        item = {
            "sku": row[0],
            "price": float(row[1]),
            "gender": row[2],
            "productSubtype": row[3],
            "color": row[4],
            "size": row[5],
            "productType": row[6],
            "isAvailable": bool(row[7])
        }
        result.append(item)

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)