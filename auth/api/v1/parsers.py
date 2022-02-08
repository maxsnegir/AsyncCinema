from flask_restful import reqparse

register_parser = reqparse.RequestParser()
register_parser.add_argument("login", type=str, required=True, help="Login is required")
register_parser.add_argument(
    "password", type=str, required=True, help="Password is required"
)
register_parser.add_argument("email", type=str, required=False)

login_parser = reqparse.RequestParser()
login_parser.add_argument("login", type=str, required=True, help="Login is required")
login_parser.add_argument(
    "password", type=str, required=True, help="Password is required"
)

create_role_parser = reqparse.RequestParser()
create_role_parser.add_argument(
    "name", type=str, required=True, help="Role name is required"
)
create_role_parser.add_argument("description", type=str, required=False)

patch_role_parser = reqparse.RequestParser()
patch_role_parser.add_argument(
    "name", type=str, required=False
)  # TODO how to make one of them required to change smth
patch_role_parser.add_argument("description", type=str, required=False)

assign_role_parser = reqparse.RequestParser()
assign_role_parser.add_argument(
    "login", type=str, required=True, help="User login required"
)
assign_role_parser.add_argument(
    "name", type=str, required=True, help="Role name is required"
)
assign_role_parser.add_argument(
    "description", type=str, required=False, help="Role description isrequired"
)
