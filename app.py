from flask import Flask, render_template, redirect, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from forms import *
from login import UserLogin

app = Flask(__name__, static_folder='static')
app.config.debug = True
app.config['SECRET_KEY'] = 'dfgd5t623@$%^&*9ghf78bjsedfi3534((%^$%#$65ndfob7687dfdfbfg'
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id, stuff=False):
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            if stuff:
                return UserLogin().employee_from_db(cursor, user_id)
            else:
                return UserLogin().client_from_db(cursor, user_id)


@app.route('/')
@app.route('/home')
def home():
    return redirect('/login')


@app.route('/client')
@login_required
def client():
    return render_template('client.html')


@app.route('/client/catalog')
@login_required
def view_catalog():
    customer = Customer(client_id=current_user.get_id())
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = customer.get_parent_category(cursor)
    return render_template('client_catalog.html', query=query)


@app.route('/client/catalog/<int:id>')
@login_required
def view_catalog_more(id):
    customer = Customer(client_id=current_user.get_id())
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = customer.get_child_category(cursor, id)
    return render_template('client_catalog_more.html', query=query)


@app.route('/client/catalog/<int:id>/category/<int:category_id>')
@login_required
def view_catalog_category(id, category_id):
    customer = Customer(client_id=current_user.get_id())
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = customer.get_child_category_more(cursor, category_id)
    return render_template('client_catalog_category.html', query=query, id=id)

#
# @app.route('/client/catalog/product/<int:id>/order')
# @login_required
# def get_order_product(id):
#     customer = Customer(client_id=current_user.get_id())
#     with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
#         with conn.cursor(cursor_factory=DictCursor) as cursor:
#             query = customer.check_product_more(cursor, id)
#     return render_template('client_catalog.html', query=query)


@app.route('/client/pp')
@login_required
def view_pp():
    customer = Customer(client_id=current_user.get_id())
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = customer.check_pp(cursor)
    return render_template('client_pp.html', query=query)


@app.route('/client/order_status')
@login_required
def view_order():
    customer = Customer(client_id=current_user.get_id())
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = customer.check_order(cursor)
    return render_template('client_order.html', query=query)


@app.route('/client/product_cart')
@login_required
def view_product_cart():
    customer = Customer(client_id=current_user.get_id())
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = customer.get_order_cart(cursor)
    return render_template('client_product_cart.html', query=query)


@app.route('/client/catalog/product/<int:id>', methods=['POST', 'GET'])
@login_required
def view_product_more(id):
    customer = Customer(client_id=current_user.get_id())
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = customer.check_characteristic_more(cursor, id)
    form = AddOrderForm()
    if form.validate_on_submit():
        count = form.count.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                count_db = customer.get_product_count(cursor, id)
                if count_db < count:
                    flash('Количество товара превышает количество товара в наличии')
                    return render_template('client_change_characteristic_detail.html', query=query, form=form)
                else:
                    customer.add_to_cart(cursor, conn, id, count)
    return render_template('client_change_characteristic_detail.html', query=query, form=form)


@app.route('/client/add_order')
@login_required
def client_add_order():
    customer = Customer(client_id=current_user.get_id())
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = customer.add_order(cursor, conn)
            customer.add_blank_order(cursor, conn)
    return redirect('/client/catalog')

    # form = AddOrderForm()
    # if form.validate_on_submit():
    #     product = form.product.data
    #     count = form.count.data
    #     with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
    #         with conn.cursor(cursor_factory=DictCursor) as cursor:
    #             count_db = customer.get_product_count(cursor, product)
    #             if count_db < count:
    #                 flash('Количество товара превышает количество товара в наличии')
    #                 return render_template('client_add_order.html', form=form)
    #             else:
    #                 customer.add_order(cursor, conn, current_user.id, product, count)
    #     return redirect('/client/order_status')
    # else:
    #     return render_template('client_add_order.html', form=form)


@app.route('/manager')
@login_required
def manager():
    return render_template('manager.html')


@app.route('/manager/orders')
def manager_view_orders():
    manager = Manager(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = manager.check_orders(cursor)
    return render_template('manager_orders.html', query=query)


@app.route('/manager/add_delivery/<int:id>', methods=['POST', 'GET'])
@login_required
def manager_add_delivery(id):
    manager = Manager(employee_id=current_user.get_id(True))
    form = DeliveryAddForm()
    if form.validate_on_submit():
        pp = form.pp.data
        cost = form.cost.data
        date = form.date.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                manager.add_delivery(cursor, conn, id, pp, cost, date)
        return redirect('/manager/orders')
    else:
        return render_template('manager_add_delivery.html', form=form)


@app.route('/manager/accept_order/<int:id>', methods=['POST', 'GET'])
@login_required
def manager_accept_order(id):
    manager = Manager(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = manager.accept_order(cursor, conn, id)
    return redirect('/manager/orders')


@app.route('/manager/pp')
@login_required
def manager_view_pp():
    manager = Manager(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = manager.check_all_pp(cursor)
    return render_template('manager_pp.html', query=query)


@app.route('/manager/change_client/<int:id>')
@login_required
def manager_view_client_more(id):
    manager = Manager(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = manager.check_client_more(cursor, id)
    return render_template('manager_change_client_detail.html', query=query)


@app.route('/manager/add_client', methods=['POST', 'GET'])
@login_required
def manager_add_client():
    manager = Manager(employee_id=current_user.get_id(True))
    form = AddClient()
    if form.validate_on_submit():
        surname = form.surname.data
        name = form.name.data
        patronymic = form.patronymic.data
        number_phone = form.number_phone.data
        login = form.login.data
        password = form.password.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                    manager.add_client(cursor, conn, surname, name, patronymic, number_phone, login, password)
        return redirect('/manager')
    else:
        return render_template('manager_add_client.html', form=form)


@app.route('/manager/change_client')
@login_required
def manager_change_client():
    manager = Manager(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = manager.get_all_client_with_statistic(cursor)
    return render_template('manager_change_client.html', query=query)


@app.route('/manager/change_client/<int:id>/update', methods=['POST', 'GET'])
@login_required
def manager_view_client_update(id):
    manager = Manager(employee_id=current_user.get_id(True))
    form = ChangeClient()
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            surname, name, patronymic, number_phone, login, password = manager.check_client_more_to_update(cursor, id)
    if form.validate_on_submit():
        surname = form.surname.data
        name = form.name.data
        patronymic = form.patronymic.data
        number_phone = form.number_phone.data
        login = form.login.data
        password = form.password.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                manager.change_client(cursor, conn, id, surname, name, patronymic, number_phone, login, password)
        return redirect('/manager')
    else:
        return render_template('manager_change_client_update.html', surname=surname, name=name, patronymic=patronymic,
                               number_phone=number_phone, login=login, password=password, form=form)

@app.route('/manager/change_client/<int:id>/del')
@login_required
def manager_view_client_del(id):
    manager = Manager(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = manager.delete_client(cursor, conn, id)
    return redirect('/manager/change_client')


@app.route('/commodity_research')
@login_required
def commodity_research():
    return render_template('commodity_research.html')


@app.route('/commodity_research/add_characteristic', methods=['POST', 'GET'])
@login_required
def commodity_research_add_characteristic():
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    form = CharacteristicsAddForm()
    if form.validate_on_submit():
        product_id = form.product.data
        size_id = form.size.data
        color_id = form.color.data
        count = form.count.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                commodity_research.add_charasteristics(cursor, conn, product_id, size_id, color_id, count)
        return redirect('/commodity_research')
    else:
        return render_template('commodity_research_add_characteristic.html', form=form)


@app.route('/commodity_research/add_product', methods=['POST', 'GET'])
@login_required
def commodity_research_add_product():
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    form = ProductAddForm()
    if form.validate_on_submit():
        brand_id = form.brand.data
        category_id = form.category.data
        description = form.description.data
        price = form.cost.data
        weight = form.weight.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                commodity_research.add_product(cursor, conn, brand_id, category_id, description, price, weight)
        return redirect('/commodity_research/change_product')
    else:
        return render_template('commodity_research_add_product.html', form=form)


@app.route('/commodity_research/add_size', methods=['POST', 'GET'])
@login_required
def commodity_research_add_size():
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    form = AddSize()
    if form.validate_on_submit():
        name = form.name.data
        standart = form.standart.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                commodity_research.add_size(cursor, conn, name, standart)
        return redirect('/commodity_research')
    else:
        return render_template('commodity_research_add_size.html', form=form)


@app.route('/commodity_research/add_color', methods=['POST', 'GET'])
@login_required
def commodity_research_add_color():
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    form = AddColor()
    if form.validate_on_submit():
        name = form.name.data
        code = form.code.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                commodity_research.add_color(cursor, conn, name, code)
        return redirect('/commodity_research')
    else:
        return render_template('commodity_research_add_color.html', form=form)


@app.route('/commodity_research/change_characteristic')
@login_required
def commodity_research_change_characteristic():
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = commodity_research.get_characteristics(cursor)
    return render_template('commodity_research_change_characteristic.html', query=query)


@app.route('/commodity_research/change_product')
@login_required
def commodity_research_change_product():
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = commodity_research.get_all_product_with_statistic(cursor)
    return render_template('commodity_research_change_product.html', query=query)


@app.route('/commodity_research/change_product/<int:id>')
@login_required
def commodity_research_view_product_more(id):
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = commodity_research.check_product_more(cursor, id)
    return render_template('commodity_research_change_product_detail.html', query=query)


@app.route('/commodity_research/change_characteristic/<int:id>')
@login_required
def commodity_research_view_characteristic_more(id):
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = commodity_research.check_characteristic_more(cursor, id)
    return render_template('commodity_research_change_characteristic_detail.html', query=query)


@app.route('/commodity_research/change_product/<int:id>/del')
@login_required
def commodity_research_view_product_del(id):
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = commodity_research.delete_product(cursor, conn, id)
    return redirect('/commodity_research/change_product')


@app.route('/commodity_research/change_characteristic/<int:id>/del')
@login_required
def commodity_research_view_characteristic_del(id):
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = commodity_research.delete_charasteristic(cursor, conn, id)
    return redirect('/commodity_research/change_characteristic')


@app.route('/commodity_research/change_characteristic/<int:id>/update', methods=['POST', 'GET'])
@login_required
def commodity_research_view_characteristic_update(id):
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            product_id, size_name, color_name, count = commodity_research.check_characteristics_more_to_update(cursor, id)
    form = CharacteristicsChangeForm(product=product_id, size=size_name, color=color_name)
    if form.validate_on_submit():
        product_id = form.product.data
        size_name = form.size.data
        color_name = form.color.data
        count = form.count.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                commodity_research.change_characteristic(cursor, conn, id, product_id, size_name, color_name, count)
        return redirect('/commodity_research')
    else:
        return render_template('commodity_research_change_characteristic_update.html', count=count, form=form)


@app.route('/commodity_research/change_product/<int:id>/update', methods=['POST', 'GET'])
@login_required
def commodity_research_view_product_update(id):
    commodity_research = CommodityResearch(employee_id=current_user.get_id(True))
    with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            brand_id, category_id, description, price, weight = commodity_research.check_product_more_to_update(cursor, id)
    form = ProductChangeForm(brand=brand_id, category=category_id)
    if form.validate_on_submit():
        brand_id = form.brand.data
        category_id = form.category.data
        description = form.description.data
        price = form.cost.data
        weight = form.weight.data
        with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                commodity_research.change_product(cursor, conn, id, brand_id, category_id, description, price, weight)
        return redirect('/commodity_research/change_product')
    else:
        return render_template('commodity_research_change_product_update.html', description=description, price=price, weight=weight,
                               form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect('/client/catalog')
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        try:
            with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    client = Login().get_user_by_email(cursor, login)
                    password_flag = True if client['password'] == password else False

        except:
            flash('Неправильный логин')
            return redirect('/login')
        if client and password_flag:
            client_login = UserLogin().create(user=client)
            login_user(client_login)
            customer = Customer(current_user.get_id())
            with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    if not customer.check_blank_order(cursor):
                        customer.add_blank_order(cursor, conn)
            return redirect('/client/catalog')
        else:
            flash('Неправильный логин')
            return redirect('/login')
    else:
        return render_template('login.html', form=form)


@app.route('/login-stuff', methods=['GET', 'POST'])
def login_stuff():
    form = LoginForm()
    if current_user.is_authenticated:
        if current_user.position == 'Менеджер':
            return redirect('/manager')
        elif current_user.position == 'Администратор':
            return redirect('/commodity_research')
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        try:
            with closing(psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST)) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    employee = Login().get_employee_by_email(cursor, login)
                    print(employee['password_employee'])
                    password_flag = True if employee['password_employee'] == password else False
        except:
            flash('Неправильный логин')
            return redirect('/login-stuff')
        if employee and password_flag:
            employee_login = UserLogin().create(user=employee)
            login_user(employee_login, True)
            if employee['position'] == 'Менеджер':
                return redirect('/manager')
            elif employee['position'] == 'Администратор':
                return redirect('/commodity_research')
        else:
            flash('Вы ввели не правильные данные')
            return redirect('/login-stuff')
    else:
        return render_template('login-stuff.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
