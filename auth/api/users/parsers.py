from flask_restplus import reqparse

change_user_data_parser = reqparse.RequestParser()
change_user_data_parser.add_argument('login', type=str, required=False)
change_user_data_parser.add_argument('email', type=str, required=False)