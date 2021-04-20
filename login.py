from flask_login import UserMixin
from sql_requests import Login


class UserLogin(UserMixin):

    def client_from_db(self, cursor, user_id):
        log = Login()
        self.__user = log.get_client(cursor, user_id)
        return self

    def employee_from_db(self, cursor, employee_id):
        log = Login()
        self.__user = log.get_employee(cursor, employee_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self, employee=False):
        return str(self.__user['id'])
