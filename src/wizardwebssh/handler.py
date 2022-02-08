# flake8: noqa
"""Handler for websocket stuffs."""
import io
import json
import logging
import os
import platform
import socket
import struct
import sys
import traceback
import weakref
from binascii import hexlify
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

import paramiko
import tornado.web
from paramiko import SSHException
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.process import cpu_count

try:
    from PyQt6 import QtCore
    from PyQt6.QtCore import QStandardPaths
    from PyQt6.QtSql import QSqlDatabase, QSqlQuery
except ImportError:
    pass
from wizardwebssh.utils import (
    UnicodeType,
    is_ip_hostname,
    is_same_primary_domain,
    is_valid_encoding,
    is_valid_hostname,
    is_valid_ip_address,
    is_valid_port,
    to_bytes,
    to_int,
    to_ip_address,
    to_str,
)
from wizardwebssh.worker import Worker, clients, recycle_worker

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError  # type: ignore

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

DELAY = 3
DEFAULT_PORT = 22

# Quickly change the default priority number for SSH default
priority = 0

swallow_http_errors = True
redirecting = None

duo_auth = False
sshdb = None
ssh_id = ""
ssh_group = ""
ssh_priority = ""
ssh_key_name = ""
ssh_config_name = ""
ssh_connection_name = ""
ssh_username = ""
ssh_password = ""
ssh_key_passphrase = ""
ssh_public_key = ""
ssh_private_key = ""
ssh_host = ""
ssh_hostname = ""
ssh_port = ""
ssh_proxy_command = ""
ssh_public_key_file = ""
ssh_private_key_file = ""
sshconfig_db = ""
default_ssh_connection_name = ""
ssh_config_hosts: List[str] = []
db_ssh_hosts: List[str] = []

# Platforms
WINDOWS = platform.system() == "Windows"
LINUX = platform.system() == "Linux"
MAC = platform.system() == "Darwin"

platform = platform.system()  # type: ignore

try:
    settings = QtCore.QSettings("WizardAssistant", "WizardAssistantDesktop")
    config_data_dir = Path("WizardAssistant/WizardAssistantDesktop")

    if settings.contains("sshconfig_db"):
        # there is the key in QSettings
        print("Checking for sshconfig_db location preference in config")
        sshconfig_db = settings.value("sshconfig_db")
        print("Found sshconfig_db in config:" + sshconfig_db)
    else:
        print("sshconfig_db not found in config. Using default")
        sshconfig_db = (
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)  # type: ignore
            / config_data_dir
            / "wizardwebssh.db"
        )
        settings.setValue("sshconfig_db", str(sshconfig_db))

    if settings.contains("ssh_connection_name"):
        # there is the key in QSettings
        print("Checking for sshconfig_db ssh_connection_name preference in config")
        default_ssh_connection_name = settings.value("ssh_connection_name")
        print("Found default_ssh_connection_name in config:" + default_ssh_connection_name)

    sshdb = QSqlDatabase.addDatabase("QSQLITE", "SSHCONFIG")
    sshdb.setDatabaseName(str(sshconfig_db))
    sshdb.open()
except Exception as e:
    print(f"Exception: {e}")

ssh_target_db = str(sshconfig_db)


def paramiko_host_info(host):
    """
    Get SSH host information via Paramiko Parser for terminal.
    Args:
        host (): SSH host from ssh config file

    Returns: dictionary with connection info parsed from config

    """
    ssh_config = paramiko.SSHConfig()
    user_config_file = os.path.expanduser("~/.ssh/config")
    if os.path.exists(user_config_file):
        with open(user_config_file) as f:
            ssh_config.parse(f)
            o = ssh_config.lookup(host)
            # print(o)
    # setup template
    con = {
        "ssh_group_name": "default",
        "ssh_connection_name": host,
        "ssh_username": "",
        "ssh_password": "",
        "Host": host,
        "HostName": "",
        "Port": "22",
        "ProxyCommand": "",
        "sshkey_name": "None",
        "sshkey_passphrase": "",
        "sshkey_public": "",
        "sshkey_private": "",
        "sshkey_public_file": "",
        "sshkey_private_file": "",
        "ssh_config_name": "paramiko",
        "ssh_config_content": "",
    }

    if o:
        if "hostname" in o.keys():
            con.update(HostName=o["hostname"])
        if "user" in o.keys():
            con.update(ssh_username=o["user"])
        # if 'identityfile' in o.keys():
        #     ident = o['identityfile']
        #     if type(ident) is list:
        #         ident = ident[0]
        #         con.update(sshkey_private_file=ident)
        # if 'key_filename' in o.keys():
        #     ident = o['identityfile']
        #     con.update(sshkey_private_file=ident)
        if "port" in o.keys():
            con.update(Port=o["port"])
        if "proxyjump" in o.keys():
            con.update(ProxyCommand=o["proxyjump"])
    print(
        f"Printing paramiko host lookup dict: {con} from {os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])))}"
    )
    return con


def get_query_as_dict(query, database_name):
    """
    Get QSqlQuery for single record as a dictionary with the columns as the keys.

    Args:
        query (): QSqlQuery to use.
        database_name (): QSqlDatabase connection or database to use.

    Returns: dictionary with key values of the query.

    """
    row_values = {}
    columns_names_mapping = {}
    try:
        # columns_names_mapping = {}
        # row_values = {}
        q = QSqlQuery(f"{query}", db=database_name)
        rec = q.record()
        if q.exec():
            if q.first():
                for column in range(rec.count()):
                    # print(column)
                    field = rec.fieldName(column)
                    value = q.value(column)
                    columns_names_mapping[field] = column
                    row_values[field] = str(value)
                # print(str(row_values))
                return row_values
    except Exception as e:
        print(f"Exception: {e}")
    return row_values


def get_default_ssh_connection_data(database_name, connection):
    """
    Gets ssh connection data for default connection.

    Args:
        database_name (): QSqlDatabase connection or database to use.
        connection (): ssh connection to get data for.

    Returns: dictionary of ssh connection data

    """
    # query = f"SELECT * from sshconfig where sshconnectionname ='{connection}'"
    query = query = f"""
                SELECT ssh_group_name, ssh_connection_name,ssh_username,ssh_password,Host,HostName,Port,ProxyCommand,
                sshkey_name,sshkey_passphrase,sshkey_public,sshkey_private,sshkey_public_file,sshkey_private_file,
                ssh_config_name,ssh_config_content
                FROM sshconnections
                JOIN sshkeys ON sshconnections.ssh_key_id = sshkeys.id
                JOIN sshgroup ON sshconnections.ssh_group_id = sshgroup.id
                JOIN sshconfig ON sshconnections.ssh_config_id = sshconfig.id
                WHERE ssh_connection_name =  '{connection}'
                """
    return get_query_as_dict(query, database_name)


def default_ssh_connection(connection, db=None):
    if db is None and sshdb is not None:
        db = sshdb
    print("============BEGIN default_ssh_connection==================")
    global ssh_id, ssh_group, ssh_priority, default_ssh_connection_name, ssh_connection_name, ssh_username, ssh_password, ssh_key_passphrase, ssh_public_key, ssh_private_key, ssh_host, ssh_hostname, ssh_port, ssh_proxy_command, ssh_key_name, ssh_config_name, ssh_public_key_file, ssh_private_key_file

    ssh_profile_dict = None

    if connection in db_ssh_hosts:
        print(f"Looking up connection {connection} via sshconfig_db")
        ssh_profile_dict = get_default_ssh_connection_data(db, connection)
        print(f"SSH Profile Dictionary from sshconfig_db : {ssh_profile_dict}")
    elif connection in ssh_config_hosts:
        print(f"Looking up connection {connection} via sshconfig parser")
        ssh_profile_dict = paramiko_host_info(connection)
        print(f"SSH Profile Dictionary from sshconfig parser: {ssh_profile_dict}")
    else:
        print(f"Connection {connection} not in db_ssh_hosts or ssh_config_hosts")

    if ssh_profile_dict is not None:
        print(f"SSH Profile Dictionary: {ssh_profile_dict}")
        ssh_group = ssh_profile_dict["ssh_group_name"]
        ssh_connection_name = ssh_profile_dict["ssh_connection_name"]
        ssh_username = ssh_profile_dict["ssh_username"]
        ssh_password = ssh_profile_dict["ssh_password"]
        ssh_host = ssh_profile_dict["Host"]
        ssh_hostname = ssh_profile_dict["HostName"]
        # print(f'Global ssh_hostname: {ssh_hostname}')
        ssh_port = ssh_profile_dict["Port"]
        ssh_proxy_command = ssh_profile_dict["ProxyCommand"]
        ssh_key_name = ssh_profile_dict["sshkey_name"]
        ssh_key_passphrase = ssh_profile_dict["sshkey_passphrase"]
        ssh_public_key = ssh_profile_dict["sshkey_public"]
        ssh_private_key = ssh_profile_dict["sshkey_private"]
        ssh_private_key_file = ssh_profile_dict["sshkey_private_file"]
        ssh_public_key_file = ssh_profile_dict["sshkey_public_file"]
        ssh_config_name = ssh_profile_dict["ssh_config_name"]
        ssh_config_content = ssh_profile_dict["ssh_config_content"]

        # Populate the ssh_private_key variable from sqlite sshconfigdb if its empty and a filename is provided instead
        if bool(ssh_private_key) is False and bool(ssh_private_key_file):
            if ssh_config_name == "default":
                with open(os.path.expanduser(ssh_private_key_file), "r") as f:
                    ssh_private_key = f.read()  # Read whole file in the file_content string
                # print(ssh_private_key)
        else:
            pass

        # update default default_ssh_connection_name with new session name
        if bool(ssh_connection_name) is not False:
            default_ssh_connection_name = ssh_connection_name
            settings.setValue("ssh_connection_name", str(default_ssh_connection_name))

    print("============End default_ssh_connection==================")


try:
    default_ssh_connection(sshdb, default_ssh_connection_name)
except Exception as e:
    print(f"Exception: {e}")


class InvalidValueError(Exception):
    pass


class SSHClient(paramiko.SSHClient):
    duo_auth = False

    def handler(self, title, instructions, prompt_list):
        answers = []
        global duo_auth

        if title.startswith("Duo two-factor login"):
            duo_auth = True
            raise SSHException("Expecting one field only.")

        for prompt_, _ in prompt_list:
            prompt = prompt_.strip().lower()
            if prompt.startswith("password"):
                answers.append(self.password)
            elif prompt.startswith("verification"):
                answers.append(self.totp)
            elif prompt.startswith("passcode"):
                answers.append(self.totp)
            else:
                raise ValueError("Unknown prompt: {}".format(prompt_))
        return answers

    def auth_interactive(self, username, handler):
        if not self.totp:
            raise ValueError("Need a verification code for 2fa.")
        self._transport.auth_interactive(username, handler)

    def _auth(self, username, password, pkey, *args):
        self.password = password
        saved_exception = None
        two_factor = False
        allowed_types = set()
        two_factor_types = {"keyboard-interactive", "password", "publickey"}

        agent = paramiko.Agent()
        try:
            agent_keys = agent.get_keys()
            # if len(agent_keys) == 0:
            # return
        except:
            pass

        for key in agent_keys:
            logging.info("Trying ssh-agent key %s" % hexlify(key.get_fingerprint()))
            try:
                self._transport.auth_publickey(username, key)
                logging.info("... success!")
                return
            except paramiko.SSHException as e:
                logging.info("... nope.")
                saved_exception = e

        if pkey is not None:
            logging.info("Trying publickey authentication")
            try:
                allowed_types = set(self._transport.auth_publickey(username, pkey))
                two_factor = allowed_types & two_factor_types
                if not two_factor:
                    return
            except paramiko.SSHException as e:
                saved_exception = e

        if duo_auth or two_factor:
            logging.info("Trying 2fa interactive auth")
            return self.auth_interactive(username, self.handler)

        if password is not None:
            logging.info("Trying password authentication")
            try:
                self._transport.auth_password(username, password)
                return
            except paramiko.SSHException as e:
                saved_exception = e
                allowed_types = set(getattr(e, "allowed_types", []))
                two_factor = allowed_types & two_factor_types

        assert saved_exception is not None
        raise saved_exception


class PrivateKey(object):
    max_length = 16384  # rough number

    tag_to_name = {"RSA": "RSA", "DSA": "DSS", "EC": "ECDSA", "OPENSSH": "Ed25519"}

    def __init__(self, privatekey, password=None, filename=""):
        self.privatekey = privatekey
        self.filename = (
            filename
            if bool(filename) is not False
            else ssh_private_key_file
            if bool(ssh_private_key_file) is not False
            else print("Unable to find Private key")
        )
        self.password = password
        self.check_length()
        self.iostr = io.StringIO(privatekey)
        self.last_exception = None

    def check_length(self):
        if len(self.privatekey) > self.max_length:
            raise InvalidValueError("Invalid key length.")

    def parse_name(self, iostr, tag_to_name):
        name = None
        for line_ in iostr:
            line = line_.strip()
            if line and line.startswith("-----BEGIN ") and line.endswith(" PRIVATE KEY-----"):
                lst = line.split(" ")
                if len(lst) == 4:
                    tag = lst[1]
                    if tag:
                        name = tag_to_name.get(tag)
                        if name:
                            break
        return name, len(line_)

    def get_specific_pkey(self, name, offset, password):
        self.iostr.seek(offset)
        logging.debug("Reset offset to {}.".format(offset))

        logging.debug("Try parsing it as {} type key".format(name))
        pkeycls = getattr(paramiko, name + "Key")
        pkey = None

        try:
            pkey = pkeycls.from_private_key(self.iostr, password=password)
        except paramiko.PasswordRequiredException:
            raise InvalidValueError("Need a passphrase to decrypt the key.")
        except (paramiko.SSHException, ValueError) as exc:
            self.last_exception = exc
            logging.debug(str(exc))

        return pkey

    def get_pkey_obj(self):
        logging.info("Parsing private key {!r}".format(self.filename))
        name, length = self.parse_name(self.iostr, self.tag_to_name)
        if not name:
            raise InvalidValueError("Invalid key {}.".format(self.filename))

        offset = self.iostr.tell() - length
        password = to_bytes(self.password) if self.password else None
        pkey = self.get_specific_pkey(name, offset, password)

        if pkey is None and name == "Ed25519":
            for name in ["RSA", "ECDSA", "DSS"]:
                pkey = self.get_specific_pkey(name, offset, password)
                if pkey:
                    break

        if pkey:
            return pkey

        logging.error(str(self.last_exception))
        msg = "Invalid key"
        if self.password:
            msg += ' or wrong passphrase "{}" for decrypting it.'.format(self.password)
        raise InvalidValueError(msg)


class MixinHandler(object):
    custom_headers = {"Server": "TornadoServer"}

    html = "<html><head><title>{code} {reason}</title></head><body>{code} " "{reason}</body></html>"

    def initialize(self, loop=None):
        self.check_request()
        self.loop = loop
        self.origin_policy = self.settings.get("origin_policy")

    def check_request(self):
        context = self.request.connection.context
        result = self.is_forbidden(context, self.request.host_name)
        self._transforms = []
        if result:
            self.set_status(403)
            self.finish(self.html.format(code=self._status_code, reason=self._reason))
        elif result is False:
            to_url = self.get_redirect_url(self.request.host_name, options.sslport, self.request.uri)
            self.redirect(to_url, permanent=True)
        else:
            self.context = context

    def check_origin(self, origin):
        if self.origin_policy == "*":
            return True

        parsed_origin = urlparse(origin)
        netloc = parsed_origin.netloc.lower()
        logging.debug("netloc: {}".format(netloc))

        host = self.request.headers.get("Host")
        logging.debug("host: {}".format(host))

        if netloc == host:
            return True

        if self.origin_policy == "same":
            return False
        elif self.origin_policy == "primary":
            return is_same_primary_domain(netloc.rsplit(":", 1)[0], host.rsplit(":", 1)[0])
        else:
            return origin in self.origin_policy

    def is_forbidden(self, context, hostname):
        ip = context.address[0]
        lst = context.trusted_downstream
        ip_address = None

        if lst and ip not in lst:
            logging.warning("IP {!r} not found in trusted downstream {!r}".format(ip, lst))
            return True

        if context._orig_protocol == "http":
            if redirecting and not is_ip_hostname(hostname):
                ip_address = to_ip_address(ip)
                if not ip_address.is_private:
                    # redirecting
                    return False

            if options.fbidhttp:
                if ip_address is None:
                    ip_address = to_ip_address(ip)
                if not ip_address.is_private:
                    logging.warning("Public plain http request is forbidden.")
                    return True

    def get_redirect_url(self, hostname, port, uri):
        port = "" if port == 443 else ":%s" % port
        return "https://{}{}{}".format(hostname, port, uri)

    def set_default_headers(self):
        for header in self.custom_headers.items():
            self.set_header(*header)

    def get_value(self, name):
        value = self.get_argument(name)
        if not value:
            raise InvalidValueError("Missing value {}".format(name))
        return value

    def get_context_addr(self):
        return self.context.address[:2]

    def get_client_addr(self):
        if options.xheaders:
            return self.get_real_client_addr() or self.get_context_addr()
        else:
            return self.get_context_addr()

    def get_real_client_addr(self):
        ip = self.request.remote_ip

        if ip == self.request.headers.get("X-Real-Ip"):
            port = self.request.headers.get("X-Real-Port")
        elif ip in self.request.headers.get("X-Forwarded-For", ""):
            port = self.request.headers.get("X-Forwarded-Port")
        else:
            # not running behind an nginx server
            return

        port = to_int(port)
        if port is None or not is_valid_port(port):
            # fake port
            port = 65535

        return (ip, port)


class NotFoundHandler(MixinHandler, tornado.web.ErrorHandler):
    def initialize(self):
        super(NotFoundHandler, self).initialize()

    def prepare(self):
        raise tornado.web.HTTPError(404)


class IndexHandler(MixinHandler, tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=cpu_count() * 5)

    def initialize(self, loop, policy, host_keys_settings):
        super(IndexHandler, self).initialize(loop)
        self.policy = policy
        self.host_keys_settings = host_keys_settings
        self.ssh_client = self.get_ssh_client()
        self.debug = self.settings.get("debug", True)
        self.font = self.settings.get("font", "")
        self.result = dict(id=None, status=None, encoding=None)

    def write_error(self, status_code, **kwargs):
        if swallow_http_errors and self.request.method == "POST":
            exc_info = kwargs.get("exc_info")
            if exc_info:
                reason = getattr(exc_info[1], "log_message", None)
                if reason:
                    self._reason = reason
            self.result.update(status=self._reason)
            self.set_status(200)
            self.finish(self.result)
        else:
            super(IndexHandler, self).write_error(status_code, **kwargs)

    def get_ssh_client(self):
        ssh = SSHClient()
        ssh._system_host_keys = self.host_keys_settings["system_host_keys"]
        ssh._host_keys = self.host_keys_settings["host_keys"]
        ssh._host_keys_filename = self.host_keys_settings["host_keys_filename"]
        ssh.set_missing_host_key_policy(self.policy)
        return ssh

    def get_privatekey(self):
        name = "privatekey"
        lst = self.request.files.get(name)
        if lst:
            # multipart form
            filename = lst[0]["filename"]
            data = lst[0]["body"]
            value = self.decode_argument(data, name=name).strip()
        else:
            # urlencoded form
            value = self.get_argument(name, "")
            filename = ""

        return value, filename

    def get_hostname(self):
        value = self.get_value("hostname")
        if not (is_valid_hostname(value) or is_valid_ip_address(value)):
            raise InvalidValueError("Invalid hostname: {}".format(value))
        return value

    def get_port(self):
        value = self.get_argument("port", "")
        if not value:
            return DEFAULT_PORT

        port = to_int(value)
        if port is None or not is_valid_port(port):
            raise InvalidValueError("Invalid port: {}".format(value))
        return port

    def lookup_hostname(self, hostname, port):
        key = hostname if port == 22 else "[{}]:{}".format(hostname, port)

        if self.ssh_client._system_host_keys.lookup(key) is None:
            if self.ssh_client._host_keys.lookup(key) is None:
                raise tornado.web.HTTPError(403, "Connection to {}:{} is not allowed.".format(hostname, port))

    def get_args(self):
        global priority, ssh_id, ssh_priority, ssh_connection_name, ssh_username, ssh_password, ssh_key_passphrase, ssh_public_key, ssh_private_key, ssh_host, ssh_hostname, ssh_port, ssh_proxy_command, ssh_public_key_file, ssh_private_key_file
        try:
            # default_ssh_connection()
            default_ssh_connection(sshdb, default_ssh_connection_name)
        except:
            pass

        hostname_form = self.get_hostname()
        port_form = self.get_port()
        username_form = self.get_value("username")
        password_form = self.get_argument("password", "")
        privatekey_form, filename = (
            self.get_privatekey()
            if bool(self.get_privatekey()) is not False
            else ssh_private_key_file
            if bool(ssh_private_key_file) is not False
            else print("Unable to find Private Key file")
        )
        passphrase_form = self.get_argument("passphrase", "")
        totp = self.get_argument("totp", "")

        # New version which defaults to form for stuff unless its empty(false)
        hostname = hostname_form if bool(hostname_form) is not False else ssh_hostname
        port = port_form if bool(port_form) is not False else ssh_port
        username = username_form if bool(username_form) is not False else ssh_username
        password = password_form if bool(password_form) is not False else ssh_password
        # privatekey = privatekey_form if bool(privatekey_form) is not False else bytes.decode(ssh_private_key) if bool(
        #    ssh_private_key) is not False else print('No Private key provided')
        privatekey = (
            privatekey_form
            if bool(privatekey_form) is not False
            else ssh_private_key
            if bool(ssh_private_key) is not False
            else print("No Private key provided")
        )
        passphrase = passphrase_form if bool(passphrase_form) is not False else ssh_key_passphrase

        if isinstance(self.policy, paramiko.RejectPolicy):
            self.lookup_hostname(hostname, port)

        if privatekey:
            pkey = PrivateKey(privatekey, passphrase, filename).get_pkey_obj()
        else:
            pkey = None

        self.ssh_client.totp = totp
        args = (hostname, port, username, password, pkey)
        logging.debug(args)

        return args

    def parse_encoding(self, data):
        try:
            encoding = to_str(data.strip(), "ascii")
        except UnicodeDecodeError:
            return

        if is_valid_encoding(encoding):
            return encoding

    def get_default_encoding(self, ssh):
        commands = ['$SHELL -ilc "locale charmap"', '$SHELL -ic "locale charmap"']

        for command in commands:
            try:
                _, stdout, _ = ssh.exec_command(command, get_pty=True)
            except paramiko.SSHException as exc:
                logging.info(str(exc))
            else:
                data = stdout.read()
                logging.debug("{!r} => {!r}".format(command, data))
                result = self.parse_encoding(data)
                if result:
                    return result

        logging.warning("Could not detect the default encoding.")
        return "utf-8"

    def ssh_connect(self, args):
        ssh = self.ssh_client
        dst_addr = args[:2]
        logging.info("Connecting to {}:{}".format(*dst_addr))

        try:
            ssh.connect(
                *args,
                allow_agent=options.allow_agent,
                look_for_keys=options.look_for_keys,
                timeout=options.timeout,
                auth_timeout=options.auth_timeout,
            )
        except socket.error:
            raise ValueError("Unable to connect to {}:{}".format(*dst_addr))
        except paramiko.BadAuthenticationType:
            raise ValueError("Bad authentication type.")
        except paramiko.AuthenticationException:
            raise ValueError("Authentication failed.")
        except paramiko.BadHostKeyException:
            raise ValueError("Bad host key.")

        term = self.get_argument("term", "") or "xterm"
        chan = ssh.invoke_shell(term=term)
        logging.info(f"Channel to channel: {chan} ")
        chan.setblocking(0)
        worker = Worker(self.loop, ssh, chan, dst_addr)
        worker.encoding = options.encoding if options.encoding else self.get_default_encoding(ssh)
        return worker

    def check_origin(self):
        event_origin = self.get_argument("_origin", "")
        header_origin = self.request.headers.get("Origin")
        origin = event_origin or header_origin

        if origin:
            if not super(IndexHandler, self).check_origin(origin):
                raise tornado.web.HTTPError(403, "Cross origin operation is not allowed.")

            if not event_origin and self.origin_policy != "same":
                self.set_header("Access-Control-Allow-Origin", origin)

    def head(self):
        pass

    def get(self):
        self.render("index.html", debug=self.debug, font=self.font)

    @tornado.gen.coroutine
    def post(self):
        if self.debug and self.get_argument("error", ""):
            # for testing purpose only
            raise ValueError("Uncaught exception")

        ip, port = self.get_client_addr()
        workers = clients.get(ip, {})
        if workers and len(workers) >= options.maxconn:
            raise tornado.web.HTTPError(403, "Too many live connections.")

        self.check_origin()

        try:
            args = self.get_args()
        except InvalidValueError as exc:
            raise tornado.web.HTTPError(400, str(exc))

        future = self.executor.submit(self.ssh_connect, args)

        try:
            worker = yield future
        except (ValueError, paramiko.SSHException) as exc:
            logging.error(traceback.format_exc())
            self.result.update(status=str(exc))
        else:
            if not workers:
                clients[ip] = workers
            worker.src_addr = (ip, port)
            workers[worker.id] = worker
            self.loop.call_later(options.delay or DELAY, recycle_worker, worker)
            self.result.update(id=worker.id, encoding=worker.encoding)

        self.write(self.result)


class WsockHandler(MixinHandler, tornado.websocket.WebSocketHandler):
    def initialize(self, loop):
        super(WsockHandler, self).initialize(loop)
        self.worker_ref = None

    def open(self):
        self.src_addr = self.get_client_addr()
        logging.info("Connected from {}:{}".format(*self.src_addr))

        workers = clients.get(self.src_addr[0])
        if not workers:
            self.close(reason="Websocket authentication failed.")
            return

        try:
            worker_id = self.get_value("id")
        except (tornado.web.MissingArgumentError, InvalidValueError) as exc:
            self.close(reason=str(exc))
        else:
            worker = workers.get(worker_id)
            if worker:
                workers[worker_id] = None
                self.set_nodelay(True)
                worker.set_handler(self)
                self.worker_ref = weakref.ref(worker)
                self.loop.add_handler(worker.fd, worker, IOLoop.READ)
            else:
                self.close(reason="Websocket authentication failed.")

    def on_message(self, message):
        logging.debug("{!r} from {}:{}".format(message, *self.src_addr))
        worker = self.worker_ref()
        try:
            msg = json.loads(message)
        except JSONDecodeError:
            return

        if not isinstance(msg, dict):
            return

        resize = msg.get("resize")
        if resize and len(resize) == 2:
            try:
                worker.chan.resize_pty(*resize)
            except (TypeError, struct.error, paramiko.SSHException):
                pass

        data = msg.get("data")
        if data and isinstance(data, UnicodeType):
            worker.data_to_dst.append(data)
            worker.on_write()

    def on_close(self):
        logging.info("Disconnected from {}:{}".format(*self.src_addr))
        if not self.close_reason:
            self.close_reason = "client disconnected"

        worker = self.worker_ref() if self.worker_ref else None
        if worker:
            worker.close(reason=self.close_reason)
