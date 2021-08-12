from datetime import date, timedelta
import psycopg2
from settings import *
from contextlib import closing
from psycopg2.extras import DictCursor
from decimal import Decimal


def db_conn(foo):
    """
    Декоратор для открытия/закрытия соединения с БД
    """

    def start_connection(*args, **kwargs):
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                foo(cursor=cursor, conn=conn, *args, **kwargs)

    return start_connection


class Login:
    """
    Класс для авторизации пользвателей
    """

    def get_client(self, cursor, user_id):
        """
        Метод для получения информации о клиение по его id
        """
        try:
            cursor.execute(f"SELECT * FROM client WHERE id = {user_id} LIMIT 1")
            res = cursor.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except:
            print("Ошибка получения данных из БД ")
        return False

    def get_employee(self, cursor, employee_id):
        """
        Метод для получения информации о сотруднике по его id
        """
        try:
            cursor.execute(f"SELECT * FROM employee WHERE employee_id = {employee_id} LIMIT 1")
            res = cursor.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except:
            print("Ошибка получения данных из БД ")
        return False

    def get_user_by_email(self, cursor, login, telephone_number=None):
        """
        Метод для получения информации о клиение по его логину
        """
        try:
            if telephone_number:
                cursor.execute(f"SELECT * FROM client WHERE login like %s or number_phone like %s LIMIT 1", (login, telephone_number))
            else:
                cursor.execute(f"SELECT * FROM client WHERE login = %s LIMIT 1", (login,))
            res = cursor.fetchone()

            if not res:
                print("Пользователь не найден")
                return False
            return res
        except:
            print("Ошибка получения данных из БД ")
        return False

    def get_employee_by_email(self, cursor, login):
        """
        Метод для получения информации о сотруднике по его логину
        """
        try:
            cursor.execute(f"SELECT * FROM employee WHERE login_employee = %s LIMIT 1", (login,))
            res = cursor.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except:
            print("Ошибка получения данных из БД ")
        return False


class BaseUser:
    """
           Класс, с общими методами для всех пользователей
    """

    def get_all_product(self, cursor):
        """
         Метод для получения ирформации обо всех продуктов
        """
        cursor.execute("""SELECT product.id, brand.name as brand_name, category.name as category_name, 
                          product.description, product.cost, product.weight FROM product 
                          INNER JOIN brand on product.brand_id = brand.id 
                          INNER JOIN category on product.category_id = category.id 
                          ORDER BY product.id""")
        query = cursor.fetchall()
        return query

    def get_characteristics(self, cursor):
        """
        Метод для получения ирформации обо всех характеристик
        """
        cursor.execute(
            """SELECT characteristics.id, brand.name as brand_name, category.name as category_name, size.name as size_name,
               color.name as color_name, characteristics.count FROM characteristics
               INNER JOIN color on characteristics.color_id = color.id
               INNER JOIN product on characteristics.product_id = product.id
               INNER JOIN size on characteristics.size_id = size.id
               INNER JOIN brand on product.brand_id = brand.id
               INNER JOIN category on product.category_id = category.id
               ORDER BY characteristics.id""")
        query = cursor.fetchall()
        return query

    def check_product_more(self, cursor, product_id):
        """
         Метод для получения ирформации об отдельном продукте
        """
        cursor.execute(
            """SELECT product.id, brand.name as brand_name, category.name as category_name, product.description, 
               product.cost, product.weight FROM product
               INNER JOIN brand on product.brand_id = brand.id
               INNER JOIN category on product.category_id = category.id
               WHERE product.id = %s""", (product_id,))
        query = cursor.fetchall()
        return query

    def get_sizes_list(self, cursor) -> list:
        """
        Метод для получения списка размеров
        """
        sizes = []
        cursor.execute('SELECT size.id, size.name FROM size ORDER BY size.name')
        for size in cursor.fetchall():
            sizes.append((size['id'], size['name']))
        return sizes

    #
    def get_colors_list(self, cursor) -> list:
        """
        Метод для получения списка цветов
        """
        colors = []
        cursor.execute('SELECT color.id, color.name FROM color ORDER BY color.name')
        for color in cursor.fetchall():
            colors.append((color['id'], color['name']))
        return colors

    def get_brands_list(self, cursor) -> list:
        """
        Метод для получении списка брендов
        """
        brands = []
        cursor.execute('SELECT brand.id, brand.name FROM brand ORDER BY brand.name')
        for b in cursor.fetchall():
            brands.append((b['id'], b['name']))
        return brands

    def get_categories_list(self, cursor, report=False) -> list:
        """
        Метод для получении списка категорий
        """
        categories = []
        # category_index = []
        cursor.execute(""" SELECT cat_1.id, cat_1.name as child_name, cat_2.name as parent_name FROM category as cat_1 
                            JOIN category as cat_2 on cat_1.parent_id = cat_2.id ORDER BY cat_1.id""")
        for category in cursor.fetchall():
            # if report:
            #     categories.append(((category['id'], ), f'{category["child_name"]} : {category["parent_name"]}'))
            categories.append((category['id'], f'{category["child_name"]} : {category["parent_name"]}'))
            # category_index.append(category['id'])
        if report:
            categories.append((0, 'Все категории'))
            # print(tuple(category_index))
        return categories

    def get_products_list(self, cursor) -> list:
        """
        Метод для получении списка продуктов
        """
        products = []
        cursor.execute("""SELECT product.id, brand.name as brand_name, category.name as category_name FROM product
               INNER JOIN brand on product.brand_id = brand.id
               INNER JOIN category on product.category_id = category.id
               where category.parent_id NOTNULL
               ORDER BY brand_name""")
        for product in cursor.fetchall():
            products.append((product['id'], f'{product["brand_name"]} {product["category_name"]}'))
        return products

    def get_pp_list(self, cursor) -> list:
        """
        Метод для получение списка пукнтов выдачи
        """
        pps = []
        cursor.execute('SELECT pp.id, pp.address FROM pickup_point as pp ORDER BY pp.address')
        for pp in cursor.fetchall():
            pps.append((pp['id'], pp['address']))
        return pps

    def get_years_list(self, cursor) -> list:
        """
        Метод для получение списка лет работы магазина
        """
        years = []
        cursor.execute("""select distinct extract(YEAR from date_of_registration) as date_of_registration from "order" 
        where order_status not like 'В корзине' """)
        for year in cursor.fetchall():
            # print(year['date_of_registration'], type(year['date_of_registration']) )
            years.append((int(year['date_of_registration'])))
        return years

    def get_months_list(self, cursor) -> list:
        """
        Метод для получение списка месяцев работы магазина
        """
        months = []
        cursor.execute("""select distinct extract(MONTH from date_of_registration) as date_of_registration from "order" 
           where order_status not like 'В корзине' """)
        for month in cursor.fetchall():
            months.append(int(month['date_of_registration']))
        current_month =int(date.today().strftime("%m"))
        if current_month not in months:
            months.append(current_month)
        return months

    def register(self, cursor, conn, surname, name, patronymic, number_phone, login, password):
        """
        Метод для добавления клиента
        """
        try:
            cursor.execute(
                """INSERT INTO client(surname, name, patronymic, number_phone, login, password)
                  values(%s,%s,%s,%s,%s,%s)""", (surname, name, patronymic, number_phone, login, password))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def check_characteristic_more(self, cursor, characteristic_id, client=False):
        """
        Метод для получении информации об отдельной характеристике товара
        """
        if client:
            cursor.execute(
                """SELECT characteristics.id, category.parent_id, category.id as category_id, brand.name as brand_name,
             category.name as category_name, size.name as size_name,color.name as color_name, 
             characteristics.count FROM characteristics
               INNER JOIN color on characteristics.color_id = color.id
               INNER JOIN product on characteristics.product_id = product.id
               INNER JOIN size on characteristics.size_id = size.id
               INNER JOIN brand on product.brand_id = brand.id
               INNER JOIN category on product.category_id = category.id
               WHERE product.id = %s""", (characteristic_id,))
        else:
            cursor.execute(
                """SELECT characteristics.id, category.parent_id, category.id as category_id, brand.name as brand_name,
             category.name as category_name, size.name as size_name,color.name as color_name, 
             characteristics.count FROM characteristics
               INNER JOIN color on characteristics.color_id = color.id
               INNER JOIN product on characteristics.product_id = product.id
               INNER JOIN size on characteristics.size_id = size.id
               INNER JOIN brand on product.brand_id = brand.id
               INNER JOIN category on product.category_id = category.id
               WHERE characteristics.id = %s""", (characteristic_id,))
        query = cursor.fetchall()
        return query


class Customer(BaseUser):
    """
    Класс для представления Покупателя
    """

    def __init__(self, client_id, surname=None, name=None):
        self.id = client_id
        self.surname = surname
        self.name = name
        self.order_id = []

    def get_information(self, cursor):
        cursor.execute(
            """SELECT login FROM client WHERE id = %s""", (self.id, ))
        query = cursor.fetchone()
        print(query, query['login'], 'sdfds')
        return query

    def get_parent_category(self, cursor):
        cursor.execute(
            """SELECT id, name FROM category WHERE parent_id ISNULL""")
        query = cursor.fetchall()
        return query

    def get_child_category(self, cursor, id):
        cursor.execute(
            """SELECT category.id, name, parent_id FROM category 
              join product on product.category_id = category.id
              WHERE parent_id = %s""", (id,))
        query = cursor.fetchall()
        return query

    def get_child_category_more(self, cursor, id):
        cursor.execute(
            """SELECT product.id, brand.name as brand_name, category.name as category_name, parent_id,
                          product.description, product.cost, product.weight FROM product 
                          INNER JOIN brand on product.brand_id = brand.id 
                          INNER JOIN category on product.category_id = category.id
                          WHERE category.id = %s 
                          ORDER BY product.id""", (id,))
        query = cursor.fetchall()
        return query

    def check_order(self, cursor):
        """
        Метод для получения информации о заказах пользавателя
        """
        cursor.execute(
            """SELECT "order".id, "order".order_status, "order".order_value, "order".date_of_registration,
               "order".completion_date FROM "order"
               WHERE "order".client_id = %s AND "order".order_status not like 'В корзине'
               ORDER BY "order".order_status
               """, (self.id,))
        query = cursor.fetchall()
        return query

    def check_pp(self, cursor):
        """
        Метод для получения информации о пунтках выдачи пользавателя
        """
        cursor.execute(
            """SELECT "order".id, pickup_point.address, pickup_point.time_start, pickup_point.time_end,
                pickup_point.number_phone_pp FROM "order"
               inner join delivery on delivery.order_id ="order".id  
               inner join pickup_point on pickup_point.id = delivery.pickup_point_id  
               WHERE "order".client_id = %s
               ORDER BY "order".date_of_registration
               DESC""", (self.id,))
        query = cursor.fetchall()
        return query

    def get_manager_id(self, cursor):
        """
        Метод для получения id менеджера
        """
        cursor.execute(
            """SELECT employee.id FROM employee
               WHERE employee.position like '%Менеджер%' """)
        query = cursor.fetchone()
        return query['id']

    def add_blank_order(self, cursor, conn):
        cursor.execute(
            """INSERT INTO "order"(client_id, order_status)
              values(%s,%s)""", (self.id, "В корзине"))
        conn.commit()

    def check_blank_order(self, cursor):
        order_id = self.get_last_order_id(cursor)
        if order_id:
            cursor.execute(
                """SELECT * from "order"
                where id = %s and order_status like 'В корзине' """, (order_id,))
            query = cursor.fetchall()
        query = None
        if query:
            return True
        else:
            return False

    def add_to_cart(self, cursor, conn, product_id, count):
        order_id = self.get_last_order_id(cursor)
        print(order_id)
        cursor.execute(
            """INSERT INTO ordering_product(order_id, product_id, quantity) values(%s, %s, %s)""",
            (order_id, product_id, count))
        conn.commit()

    def get_last_order_id(self, cursor):
        cursor.execute("""SELECT id from "order" where client_id = %s order by "order".id""", (self.id,))
        order_query = cursor.fetchall()
        if order_query:
            order_id = order_query[-1]['id']
            return order_id
        else:
            return None

    def get_order_cart(self, cursor):
        order_id = self.get_last_order_id(cursor)
        cursor.execute("""SELECT ordering_product.id as op_id, brand.name as brand_name, category.name as category_name,
         quantity, cost, product_id as p_id from ordering_product
         inner join  product on product.id = ordering_product.product_id
         inner join  category on product.category_id = category.id
         inner join  brand on product.brand_id = brand.id
         where order_id = %s""", (order_id,))
        query = cursor.fetchall()
        return query

    def add_order(self, cursor, conn):
        """
        Метод для добавления заказа
        """
        employee_id = self.get_manager_id(cursor)
        order_id = self.get_last_order_id(cursor)
        order_value = Decimal('0')
        order_cart = self.get_order_cart(cursor)
        for row in order_cart:
            order_value += row['cost'] * row['quantity']
            cursor.execute(
                """UPDATE characteristics SET count = count - %s
                    WHERE characteristics.product_id = %s""", (row['quantity'], row['p_id']))
            conn.commit()

        cursor.execute("""SELECT amount_of_discount from client
                JOIN discounts on client.discount_id = discounts.id
                 where client.id = %s""", (self.id,))
        query = cursor.fetchone()
        if query:
            discount = int(query['amount_of_discount'])
            order_value *= Decimal((100-discount)/100)
            order_value = order_value.quantize(Decimal("1.00"))
        date_of_registration = date.today().strftime("%Y.%m.%d")
        cursor.execute(
            """Update "order" set employee_id = %s, order_value = %s, order_status = %s,  date_of_registration = %s
                  where "order".id = %s""", (employee_id, order_value, "В обработке", date_of_registration, order_id))
        conn.commit()

        cursor.execute("""select  count(client_id), sum(order_value) as sum_value from "order"
                where order_status not like('В корзине') and client_id = %s
                group by client_id""", (self.id, ))
        total_value = cursor.fetchone()['sum_value']
        cursor.execute("""select * from discounts;""", (self.id,))
        discounts_query = cursor.fetchall()
        discount_id = None
        for row in discounts_query:
            if total_value > row['sum_orders']:
                discount_id = row['id']
        if discount_id:
            cursor.execute(
                """Update client set discount_id = %s where client.id = %s""", (discount_id, self.id))
            conn.commit()


    def get_product_count(self, cursor, product_id):
        """
        Метод для получения количества определеного товара
        """
        try:
            cursor.execute(
                """SELECT characteristics.count FROM product
                 INNER JOIN characteristics on characteristics.product_id = product.id
                 WHERE product.id = %s """, (product_id,))
            count_query = cursor.fetchone()
            count = count_query['count']
            return count
        except:
            print('ввели не правильные данные')


class Manager(BaseUser):
    """
               Класс для представления Менеджера
    """

    def __init__(self, employee_id, surname=None, name=None):
        self.id = employee_id
        self.surname = surname
        self.name = name

    def add_delivery(self, cursor, conn, order_id, pp_id, cost, date_delivery):
        """
        Метод для добавления доставки
        """
        try:
            cursor.execute(
                """SELECT (product.weight * ordering_product.quantity) as total_weight FROM "order"
              inner join ordering_product on ordering_product.order_id ="order".id  
               inner join product on ordering_product.product_id = product.id  
            WHERE "order".id = %s """, (order_id,))
            weight_query = cursor.fetchall()
            weight = 0
            for w in weight_query:
                weight += w['total_weight']
            cursor.execute(
                """INSERT INTO delivery(order_id, pickup_point_id, delivery_cost, sum_weight,  date_delivery)
                 values(%s,%s,%s,%s,%s)""", (order_id, pp_id, cost, weight, date_delivery))
            conn.commit()
            cursor.execute(
                """update "order" set order_status = 'В пути' where "order".id = %s """, (order_id,))
            conn.commit()
            cursor.execute(
                """update "order" set completion_date = %s where "order".id = %s """, (date_delivery, order_id,))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def accept_order(self, cursor, conn, id):
        """"
        Метод для принятия заказа
        """
        try:
            cursor.execute(
                """update "order" set order_status = 'Принят' where "order".id = %s """, (id,))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def check_orders(self, cursor):
        """
        Метод для получении иноформации обо всех заказов для данного менежера
        """
        cursor.execute(
            """SELECT "order".id, client.surname, client.name, client.patronymic,  "order".order_status, 
            "order".order_value,  "order".date_of_registration, "order".completion_date FROM "order"
               inner join client on client.id ="order".client_id  
               WHERE "order".employee_id = %s
               ORDER BY "order".completion_date desc, "order".order_status 
               """, (self.id,))
        query = cursor.fetchall()
        return query

    def orders_report(self, cursor):
        """
        Метод для получении иноформации обо всех заказов для данного менежера
        """
        # d1 = date.today()
        d1 = date(2021, 4, 15)  # период с выполнеными заказами
        d3 = d1 - timedelta(days=3)
        cursor.execute(
            """SELECT "order".id, client.surname, client.name, client.patronymic,  "order".order_status, 
            "order".order_value,  "order".date_of_registration, "order".completion_date FROM "order"
               inner join client on client.id ="order".client_id  
               WHERE "order".employee_id = %s  AND date_of_registration BETWEEN %s AND %s
               ORDER BY "order".completion_date desc, "order".order_status
               """, (self.id, d3, d1))
        query = cursor.fetchall()
        return query

    def customers_report(self, cursor, year):
        """
        Метод для получении иноформации обо всех заказов для данного менежера
        """
        cursor.execute(
            """with sum_client_order as (select client_id, count(client_id), sum(order_value) as sum_value from "order"
                where order_status not like('В корзине') and  extract(year from date_of_registration) =  %s
                group by client_id)
                select client.id, client.surname, client.name, client.patronymic,
                coalesce("count", 0) as "count", coalesce(sum_value, 0) as sum_value, coalesce(amount_of_discount, 0) as discount from client
                left join sum_client_order on client.id = sum_client_order.client_id
                left join discounts on client.discount_id = discounts.id
                order by "count"
                desc
               """, (year,))
        query = cursor.fetchall()
        return query

    def check_all_pp(self, cursor):
        """
        Метод для получении иноформации обо всех пунктах выдачи
        """
        cursor.execute(
            """SELECT pickup_point.address, pickup_point.time_start, pickup_point.time_end, 
            pickup_point.number_phone_pp  FROM pickup_point""")
        query = cursor.fetchall()
        return query

    def delete_client(self, cursor, conn, id):
        """
        Метод для удаления клиента
        """
        try:
            cursor.execute(
                """delete from  client where client.id = %s """, (id,))
            conn.commit()
        except:
            print('такого пользователя не существует')

    def add_client(self, cursor, conn, surname, name, patronymic, number_phone, login, password):
        """
        Метод для добавления клиента
        """
        try:
            cursor.execute(
                """INSERT INTO client(surname, name, patronymic, number_phone, login, password)
                  values(%s,%s,%s,%s,%s,%s)""", (surname, name, patronymic, number_phone, login, password))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def change_client(self, cursor, conn, id, surname, name, patronymic, phone, log, psw):
        """
        Метод для изменения клиента
        """
        try:
            cursor.execute(
                """update client set surname = %s, name = %s, patronymic = %s,  number_phone = %s, login = %s, password = %s
                  where client.id = %s """, (surname, name, patronymic, phone, log, psw, id))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def get_all_clients(self, cursor):
        """
        Метод для получения ирформации о всех характеристик
        """
        cursor.execute(
            """SELECT client.id, client.surname, client.name, client.patronymic,  client.number_phone, client.login,
              client.password FROM client order by client.id""")
        query = cursor.fetchall()
        return query

    def check_client_more_to_update(self, cursor, client_id):
        """
        Метод для получения ирформации об отдельном клиенте
        """
        cursor.execute(
            """SELECT client.surname, client.name, client.patronymic,  client.number_phone, client.login,  client.password FROM client
               WHERE client.id = %s """, (client_id,))
        query = cursor.fetchone()
        return query['surname'], query['name'], query['patronymic'], query['number_phone'], query['login'], query[
            'password']

    def check_client_more(self, cursor, client_id):
        """
        Метод для получения ирформации об отдельном клиенте для его изменения
        """
        cursor.execute(
            """SELECT client.id, client.surname, client.name, client.patronymic,  client.number_phone, client.login,  client.password FROM client
               WHERE client.id = %s """, (client_id,))
        query = cursor.fetchall()
        return query


class CommodityResearch(BaseUser):
    """
    Класс для представления Администратора
    """

    def __init__(self, employee_id, surname=None, name=None):
        self.id = employee_id
        self.surname = surname
        self.name = name

    def products_report(self, cursor, category_id, month):
        try:
            # print(category_id)
            if isinstance(category_id, int):
                if category_id == 0:
                    category_id = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                else:
                    category_id = (category_id, )
            cursor.execute(
                """with sum_order_product as (select product_id, sum(quantity) from ordering_product
                join "order" on ordering_product.order_id = "order".id 
                where extract(month from date_of_registration) = %s group by product_id) 
                 select product.id, brand.name as brand_name, category.name as category_name, 
                product.description, product.cost, product.weight, coalesce("sum", 0) as "sum",
                 "characteristics".count from product 
                left join sum_order_product on product.id = sum_order_product.product_id
                join brand on product.brand_id = brand.id
                join category on product.category_id = category.id
                join "characteristics" on product.id = "characteristics".product_id
                 where category.id in %s
                order by "sum"
                desc  """, (month, category_id))
            query = cursor.fetchall()
            return query
        except:
            print('ошибка')

    def delete_product(self, cursor, conn, id):
        """
        Метод для удаления продукта
        """
        try:
            cursor.execute(
                """delete from product where product.id = %s """, (id,))
            conn.commit()
        except:
            print('такого продукта не существует')

    def delete_charasteristic(self, cursor, conn, id):
        """
        Метод для удаления характеристики товара
        """
        try:
            cursor.execute(
                """delete from charasteristics where charasteristics.id = %s """, (id,))
            conn.commit()
        except:
            print('такого продукта не существует')

    def add_size(self, cursor, conn, name, standart):
        """
        Метод для добавления размера
        """
        try:
            cursor.execute(
                """INSERT INTO size(name, standart) values(%s, %s)""", (name, standart))
            conn.commit()
        except:
            print('проверьте данные')

    def add_color(self, cursor, conn, name, code):
        """
        Метод для добавления цвета
        """
        try:
            cursor.execute(
                """INSERT INTO color(name, code) values(%s, %s)""", (name, code))
            conn.commit()
        except:
            print('проверьте данные')

    def add_product(self, cursor, conn, brand_id, category_id, description, cost, weight):
        """
        Метод для добавления товара
        """
        try:
            cursor.execute(
                """INSERT INTO product(brand_id, category_id, description, cost, weight)
                  values(%s,%s,%s,%s,%s)""", (brand_id, category_id, description, cost, weight))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def add_charasteristics(self, cursor, conn, product_id, size_id, color_id, count):
        """
        Метод для добавления характеристики товара
        """
        try:
            cursor.execute(
                """INSERT INTO characteristics(product_id, size_id, color_id, count)
                  values(%s,%s,%s,%s)""", (product_id, size_id, color_id, count))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def change_characteristic(self, cursor, conn, id, product_id, size_id, color_id, count):
        """
        Метод для изменения характеристики товара
        """
        try:
            cursor.execute(
                """update characteristics set product_id = %s, size_id = %s, color_id = %s,  count = %s
                  where characteristics.id = %s """, (product_id, size_id, color_id, count, id))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def change_product(self, cursor, conn, id, brand_id, category_id, description, cost, weight):
        """
        Метод для изменения товара
        """
        try:
            cursor.execute(
                """update product set brand_id = %s, category_id = %s, description = %s, cost = %s, weight = %s
                  where product.id = %s """, (brand_id, category_id, description, cost, weight, id))
            conn.commit()
        except:
            print('ввели не правильные данные')

    def check_product_more_to_update(self, cursor, product_id):
        """
        Метод для получения ирформации о  характеристики отдельного товара
        """
        cursor.execute("""SELECT  brand.id as brand_id, category.id as category_id,
                 product.description, product.cost, product.weight FROM product
                       INNER JOIN brand on product.brand_id = brand.id
                       INNER JOIN category on product.category_id = category.id
                   WHERE product.id = %s""", (product_id,))
        query = cursor.fetchone()
        return query['brand_id'], query['category_id'], query['description'], query['cost'], query['weight']

    def check_characteristics_more_to_update(self, cursor, characteristic_id):
        """
        Метод для получения ирформации об отдельной характеристики для ее изменения
        """
        cursor.execute(
            """SELECT product.id as product_id, size.id as size_id, color.id as color_id, 
               characteristics.count FROM characteristics
               INNER JOIN color on characteristics.color_id = color.id
               INNER JOIN product on characteristics.product_id = product.id
               INNER JOIN size on characteristics.size_id = size.id
               WHERE characteristics.id = %s
               ORDER BY characteristics.id""", (characteristic_id,))
        query = cursor.fetchone()
        return [query['product_id'], query['size_id'], query['color_id'], query['count']]

    def check_product_more(self, cursor, product_id):
        """
        Метод для получения ирформации об отдельном продукте для его изменения
        """
        cursor.execute("""SELECT product.id, brand.name as brand_name, category.name as category_name,
         product.description, product.cost, product.weight FROM product
               INNER JOIN brand on product.brand_id = brand.id
               INNER JOIN category on product.category_id = category.id
           WHERE product.id = %s 
            ORDER BY brand_name""", (product_id,))
        query = cursor.fetchall()
        return query
