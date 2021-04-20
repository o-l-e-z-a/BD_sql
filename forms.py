from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, IntegerField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from sql_requests import *


class ProductForm(FlaskForm):
    base_user = BaseUser()
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            brands = base_user.get_brands_list(cursor)
            categories = base_user.get_categories_list(cursor)
    brand = SelectField('Бренд:', choices=brands, coerce=int)
    category = SelectField('Категория:', choices=categories, coerce=int)
    description = StringField('Описание: ', validators=[Length(min=0, max=1000000)])
    cost = DecimalField('Цена: ')
    weight = DecimalField('Вес: ') # validators=[Length(message='Вы ввели не целое число')]


class ProductChangeForm(ProductForm):
    submit = SubmitField('изменить')


class ProductAddForm(ProductForm):
    submit = SubmitField('добавить')


class AddColor(FlaskForm):
    name = StringField('Название: ', validators=[Length(min=3, max=30)])
    code = StringField('Код: ', validators=[Length(min=3, max=6)])
    submit = SubmitField('добавить')


class AddSize(FlaskForm):
    name = StringField('Название: ', validators=[Length(min=1, max=30)])
    standart = StringField('Стандарт: ', validators=[Length(min=3, max=30)])
    submit = SubmitField('добавить')


class Client(FlaskForm):
    surname = StringField('Фамилия:',  validators=[Length(min=3, max=30)])
    name = StringField('Имя: ', validators=[Length(min=3, max=30)])
    patronymic = StringField('Отчество: ', validators=[Length(min=3, max=30)])
    number_phone = StringField('Телефон: ')
    login = StringField('Email: ', validators=[Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4, max=100, message='Введите пароль, длиной от 4 '
                                                                                       'до 100 символов')])


class AddClient(Client):
    submit = SubmitField('добавить')


class ChangeClient(Client):
    submit = SubmitField('изменить')


class CharacteristicsForm(FlaskForm):
    base_user = BaseUser()
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            products = base_user.get_products_list(cursor)
            colors = base_user.get_colors_list(cursor)
            sizes = base_user.get_sizes_list(cursor)
    product = SelectField('Продукт:', choices=products)
    color = SelectField('Цвет:', choices=colors)
    size = SelectField('Размер:', choices=sizes)
    count = IntegerField('Количество:')
#
#
class CharacteristicsAddForm(CharacteristicsForm):
    submit = SubmitField('добавить')


class CharacteristicsChangeForm(CharacteristicsForm):
    submit = SubmitField('изменить')


class LoginForm(FlaskForm):
    login = StringField('Email: ', validators=[Email()])
    password = PasswordField('Пароль:',
                             validators=[DataRequired(), Length(min=4, max=100, message='Введите пароль, длиной от 4 '
                                                                                        'до 100 символов')])
    submit = SubmitField('Войти')


class DeliveryAddForm(FlaskForm):
    base_user = BaseUser()
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            pps = base_user.get_pp_list(cursor)
    pp = SelectField('Пункт доставки:', choices=pps)
    cost = DecimalField('Цена: ')
    date = DateField('Дата: ')
    submit = SubmitField('Добавить')


class AddOrderForm(FlaskForm):
    # base_user = BaseUser()
    # with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
    #     with conn.cursor(cursor_factory=DictCursor) as cursor:
    #         products = base_user.get_products_list(cursor)
    # product = SelectField('Продукт:', choices=products)
    count = IntegerField('Количество: ')
    submit = SubmitField('Добавить в корзину')


