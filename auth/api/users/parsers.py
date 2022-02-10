from flask_restplus import reqparse

change_user_data_parser = reqparse.RequestParser()
change_user_data_parser.add_argument('login', type=str, required=False)
change_user_data_parser.add_argument('email', type=str, required=False)

auth_history_parser = reqparse.RequestParser()
auth_history_parser.add_argument('page_number', type=int, default=0, required=False)
auth_history_parser.add_argument('page_size', type=int, default=10, required=False)
