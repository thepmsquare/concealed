import configparser
import os

config = configparser.ConfigParser()
config_file_path = (
        os.path.dirname(os.path.abspath(__file__)) + os.sep + "data" + os.sep + "config.ini"
)
config.read(config_file_path)

# get all vars and typecast
cstr_message_appended_at_end = config.get("GENERAL", "MSG_APPENDED_AT_THE_END")
cstr_salt = config.get("GENERAL", "SALT")
