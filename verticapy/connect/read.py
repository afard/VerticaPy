"""
(c)  Copyright  [2018-2023]  OpenText  or one of its
affiliates.  Licensed  under  the   Apache  License,
Version 2.0 (the  "License"); You  may  not use this
file except in compliance with the License.

You may obtain a copy of the License at:
http://www.apache.org/licenses/LICENSE-2.0

Unless  required  by applicable  law or  agreed to in
writing, software  distributed  under the  License is
distributed on an  "AS IS" BASIS,  WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied.
See the  License for the specific  language governing
permissions and limitations under the License.
"""
import os

# VerticaPy Modules
from verticapy.errors import ParameterError
from verticapy.connect.connect import VERTICAPY_AUTO_CONNECTION, SESSION_LABEL
from verticapy.connect.utils import get_confparser


def available_connections():
    """
Displays all the available connections.

Returns
-------
list
    all the available connections.
    """
    confparser = get_confparser()
    if confparser.has_section(VERTICAPY_AUTO_CONNECTION):
        confparser.remove_section(VERTICAPY_AUTO_CONNECTION)
    all_connections = confparser.sections()
    return all_connections


available_auto_connection = available_connections


def read_dsn(section: str, dsn: str = ""):
    """
Reads the DSN information from the VERTICAPY_CONNECTIONS environment 
variable or the input file.

Parameters
----------
section: str
    Name of the section in the configuration file.
dsn: str, optional
    Path to the file containing the credentials. If empty, the 
    VERTICAPY_CONNECTIONS environment variable will be used.

Returns
-------
dict
    dictionary with all the credentials.
    """
    confparser = get_confparser(dsn)

    if confparser.has_section(section):

        options = confparser.items(section)
        conn_info = {
            "port": 5433,
            "user": "dbadmin",
            "session_label": SESSION_LABEL,
        }

        env = False
        for option_name, option_val in options:
            if option_name.lower().startswith("env"):
                if option_val.lower() in ("true", "t", "yes", "y"):
                    env = True
                break

        for option_name, option_val in options:

            option_name = option_name.lower()

            if option_name in ("pwd", "password", "uid", "user") and env:
                if option_name == "pwd":
                    option_name = "password"
                elif option_name == "uid":
                    option_name = "user"
                if os.getenv(option_val) != None:
                    conn_info[option_name] = os.getenv(option_val)
                else:
                    raise ParameterError(
                        f"The '{option_name}' environment variable "
                        f"'{option_val}' does not exist and the 'env' "
                        "option is set to True.\nImpossible to set up "
                        "the final DSN.\nTips: You can manually set "
                        "it up by importing os and running the following "
                        f"command:\nos.environ['{option_name}'] = '******'"
                    )

            elif option_name in ("servername", "server"):
                conn_info["host"] = option_val

            elif option_name == "uid":
                conn_info["user"] = option_val

            elif (option_name in ("port", "connection_timeout")) and (
                option_val.isnumeric()
            ):
                conn_info[option_name] = int(option_val)

            elif option_name == "pwd":
                conn_info["password"] = option_val

            elif option_name == "backup_server_node":
                backup_server_node = {}
                exec(f"id_port = '{option_val}'", {}, backup_server_node)
                conn_info["backup_server_node"] = backup_server_node["id_port"]

            elif option_name == "kerberosservicename":
                conn_info["kerberos_service_name"] = option_val

            elif option_name == "kerberoshostname":
                conn_info["kerberos_host_name"] = option_val

            elif "vp_test_" in option_name:
                conn_info[option_name[8:]] = option_val

            elif option_name in (
                "ssl",
                "autocommit",
                "use_prepared_statements",
                "connection_load_balance",
                "disable_copy_local",
            ):
                option_val = option_val.lower()
                conn_info[option_name] = option_val in ("true", "t", "yes", "y")

            elif option_name != "session_label" and not (option_name.startswith("env")):
                conn_info[option_name] = option_val

        return conn_info

    else:

        raise NameError(f"The DSN Section '{section}' doesn't exist.")
