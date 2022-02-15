from api.admin import admin_namespace as namespace

register_parser = namespace.parser()
register_parser.add_argument("login", type=str, required=True, help="Login is required", location="form")
register_parser.add_argument("password", type=str, required=True, help="Password is required", location="form")
register_parser.add_argument("email", type=str, required=True, help="Email is required", location="form")

login_parser = namespace.parser()
login_parser.add_argument("login", type=str, required=True, help="Login is required", location="form")
login_parser.add_argument("password", type=str, required=True, help="Password is required", location="form")

change_password_parser = namespace.parser()
change_password_parser.add_argument('current_password', type=str, required=True, help='Wrong Password',
                                    location="form")
change_password_parser.add_argument('new_password', type=str, required=True, help='Wrong Password', location="form")

role_parser = namespace.parser()
role_parser.add_argument('name', type=str, required=True, help='Role name is required', location="form")
role_parser.add_argument('description', type=str, required=False, location="form")

change_role_parser = namespace.parser()
change_role_parser.add_argument("name", type=str, required=False, location="form")
change_role_parser.add_argument("description", type=str, required=False, location="form")
