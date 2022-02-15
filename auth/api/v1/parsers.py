from api.v1 import user_namespace

change_user_data_parser = user_namespace.parser()
change_user_data_parser.add_argument('login', type=str, required=False, location="form")
change_user_data_parser.add_argument('email', type=str, required=False, location="form")

auth_history_parser = user_namespace.parser()
auth_history_parser.add_argument('page_number', type=int, default=0, required=False)
auth_history_parser.add_argument('page_size', type=int, default=10, required=False,)
