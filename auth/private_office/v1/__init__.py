from flask_restful import reqparse

register_parser = reqparse.RequestParser()
register_parser.add_argument('login', type=str, required=True, help='Login is required')
register_parser.add_argument('password', type=str, required=True, help='Password is required')
register_parser.add_argument('email', type=str, required=False)

login_parser = reqparse.RequestParser()
login_parser.add_argument('login', type=str, required=True, help='Login is required')
login_parser.add_argument('password', type=str, required=True, help='Password is required')

change_login_parser = reqparse.RequestParser()
change_login_parser.add_argument('new_login', type=str, required=True, help='New login is required')

change_password_parser = reqparse.RequestParser()
change_password_parser.add_argument('new_password', type=str, required=True, help='New password is required')
