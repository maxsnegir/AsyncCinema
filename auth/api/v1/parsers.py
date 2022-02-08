from flask_restful import reqparse

register_parser = reqparse.RequestParser()
register_parser.add_argument('login', type=str, required=True, help='Login is required')
register_parser.add_argument('password', type=str, required=True, help='Password is required')
register_parser.add_argument('email', type=str, required=True)

login_parser = reqparse.RequestParser()
login_parser.add_argument('login', type=str, required=True, help='Login is required')
login_parser.add_argument('password', type=str, required=True, help='Password is required')

change_password_parser = reqparse.RequestParser()
change_password_parser.add_argument('current_password', type=str, required=True, help='Wrong Password')
change_password_parser.add_argument('new_password', type=str, required=True, help='Wrong Password')

change_user_data_parser = reqparse.RequestParser()
change_user_data_parser.add_argument('login', type=str, required=False)
change_user_data_parser.add_argument('email', type=str, required=False)
