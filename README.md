# BD_sql

## Проект для изучения БД и SQL-запросов, цель - интерфейс и проектированние БД интернет-магазина одежды. Даталогическая схема в файле schema.jpg. Использовался Flask с чистыми SQL-запросами без ORM. Включает следующий функционал:
### Для покупателя:
  - регистрация/авторизация
  - просмотр каталога товаров по категориям с возможностью добавления в корзину
  - просмотр и редактирование корзины
  - оформление заказа
  - просмотр всех заказов, а также детальный просмотр конкретного заказа
  - просмотр пунктов выдачи, указанных в заказе
 ### Для менеджера по заказам:
  - Просмотр всех заказов, относящихся к конкретному менеджеру, с возможностью передачи в доставку
  - просмотр каталога товаров по категориям с возможностью добавления в корзину
  - CRUD клиентов (если клиент оформил заказ по телефону, менеджер его регистрирует в системе)
  - отчет по заявкам клиентов за 3 последних дня
  - отчет по заказам клиентов ( кол-во заказов, итоговая стоимость, размер скидки для каждого клиента)
  ### Товаровед:
  - CRUD товаров
  - CRUD характеристик товара
  - добавление размера
  - добавление цвета
  - отчет по проданным товарам (выбор месяца и категории товара -> кол-во покупок и кол-во в наличии)
 
