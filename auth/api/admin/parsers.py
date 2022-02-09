from flask_restplus import reqparse

register_parser = reqparse.RequestParser()
register_parser.add_argument("login", type=str, required=True, help="Login is required")
register_parser.add_argument("password", type=str, required=True, help="Password is required")
register_parser.add_argument("email", type=str, required=True, help="Email is required")

login_parser = reqparse.RequestParser()
login_parser.add_argument("login", type=str, required=True, help="Login is required")
login_parser.add_argument("password", type=str, required=True, help="Password is required")

change_password_parser = reqparse.RequestParser()
change_password_parser.add_argument('current_password', type=str, required=True, help='Wrong Password')
change_password_parser.add_argument('new_password', type=str, required=True, help='Wrong Password')

role_parser = reqparse.RequestParser()
role_parser.add_argument('name', type=str, required=True, help='Role name is required')
role_parser.add_argument('description', type=str, required=False)

change_role_parser = reqparse.RequestParser()
change_role_parser.add_argument("name", type=str, required=False)
change_role_parser.add_argument("description", type=str, required=False)
