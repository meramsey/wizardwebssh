## Wizard Web SSH

[![ci](https://github.com/meramsey/wizardwebssh/workflows/ci/badge.svg)](https://github.com/meramsey/wizardwebssh/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://meramsey.github.io/wizardwebssh/)
[![pypi version](https://img.shields.io/pypi/v/wizardwebssh.svg)](https://pypi.org/project/wizardwebssh/)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/wizardwebssh/community)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Web based ssh client

## Requirements

wizardwebssh requires Python 3.6 or above.

<details>
<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.6
pyenv install 3.6.12

# make it available globally
pyenv global system 3.6.12
```
</details>

## Installation

With `pip`:
```bash
python3.6 -m pip install wizardwebssh
```

With [`pipx`](https://github.com/pipxproject/pipx):
```bash
python3.6 -m pip install --user pipx

pipx install --python python3.6 wizardwebssh
```

### Introduction

A simple web application to be used as an ssh client to connect to your ssh servers. It is written in Python, base on tornado, paramiko and xterm.js.

### Features

* SSH password authentication supported, including empty password.
* SSH public-key authentication supported, including DSA RSA ECDSA Ed25519 keys.
* SSH Agent Support
* Sqlite DB support for SSH Config.
* PyQT5 MultiTabbed Terminal Widget for embedding into PyQT5 apps.
* Encrypted keys supported.
* Two-Factor Authentication (time-based one-time password, Duo Push Auth) supported.
* Fullscreen terminal supported.
* Terminal window resizable.
* Auto detect the ssh server's default encoding.
* Modern browsers including Chrome, Firefox, Safari, Edge, Opera supported.


### Preview

![Login](https://gitlab.com/mikeramsey/wizardwebssh/raw/master/preview/login.png)
![Terminal](https://gitlab.com/mikeramsey/wizardwebssh/raw/master/preview/terminal.png)
![PyQT5 MultiTabbed Terminal Widget](https://gitlab.com/mikeramsey/wizardwebssh/raw/master/preview/multitabbedterminalwidget.png)
![PyQT5 MultiTabbed DarkMode Terminal Widget](https://gitlab.com/mikeramsey/wizardwebssh/raw/master/preview/TabbedTerminal_Example1.png)
![PyQT5 MultiTabbed DarkMode Terminal Widget Login](https://gitlab.com/mikeramsey/wizardwebssh/raw/master/preview/TabbedTerminal_Example2.png)


### How it works
```
+---------+     http     +--------+    ssh    +-----------+
| browser | <==========> | wizardwebssh | <=======> | ssh server|
+---------+   websocket  +--------+    ssh    +-----------+
```

### Requirements

* Python 2.7/3.4+


### Quickstart

1. Install this app, run command `pip install wizardwebssh`
2. Start a webserver, run command `wssh`
3. Open your browser, navigate to `127.0.0.1:8889`
4. Input your data, submit the form.


### Server options

```bash
# start a http server with specified listen address and listen port
wssh --address='2.2.2.2' --port=8000

# start a https server, certfile and keyfile must be passed
wssh --certfile='/path/to/cert.crt' --keyfile='/path/to/cert.key'

# missing host key policy
wssh --policy=reject

# logging level
wssh --logging=debug

# log to file
wssh --log-file-prefix=main.log

# more options
wssh --help
```

### Browser console

```javascript
// connect to your ssh server
wssh.connect(hostname, port, username, password, privatekey, passphrase, totp);

// pass an object to wssh.connect
var opts = {
  hostname: 'hostname',
  port: 'port',
  username: 'username',
  password: 'password',
  privatekey: 'the private key text',
  passphrase: 'passphrase',
  totp: 'totp'
};
wssh.connect(opts);

// without an argument, wssh will use the form data to connect
wssh.connect();

// set a new encoding for client to use
wssh.set_encoding(encoding);

// reset encoding to use the default one
wssh.reset_encoding();

// send a command to the server
wssh.send('ls -l');
```

### Custom Font

To use custom font, put your font file in the directory `wizardwebssh/static/css/fonts/` and restart the server.

### URL Arguments

Support passing arguments by url (query or fragment) like following examples:

Passing form data (password must be encoded in base64, privatekey not supported)
```bash
http://localhost:8889/?hostname=xx&username=yy&password=str_base64_encoded
```

Passing a terminal background color
```bash
http://localhost:8889/#bgcolor=green
```

Passing a user defined title
```bash
http://localhost:8889/?title=my-ssh-server
```

Passing an encoding
```bash
http://localhost:8889/#encoding=gbk
```

Passing a command executed right after login
```bash
http://localhost:8889/?command=pwd
```

Passing a terminal type
```bash
http://localhost:8889/?term=xterm-256color
```

### Use Pyqt5 SSH Terminal Widget

Start up the wizardwebssh ssh service
```
class WizardWebssh(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            # Start WebSSH Service in background.
            print('Starting SSH websocket server in the background')
            import asyncio

            asyncio.set_event_loop(asyncio.new_event_loop())
            from wizardwebssh.main import main as wssh
            wssh()
            print('Stopped SSH websocket server in the background')
            QApplication.processEvents()
            time.sleep(self.interval)


    wizardwebssh_service = WizardWebssh()
    time.sleep(.300)
```

Embed the widget as desired
```
    win = TabbedTerminal()
    win.show()
```

Review tabbedbterminal.py for full standalone working example of SSH terminal widget.


### Use Docker

Start up the app
```
docker-compose up
```

Tear down the app
```
docker-compose down
```

### Tests

Requirements
```
pip install pytest pytest-cov codecov flake8 mock
```

Use unittest to run all tests
```
python -m unittest discover tests
```

Use pytest to run all tests
```
python -m pytest tests
```

### Deployment

Running behind an Nginx server

```bash
wssh --address='127.0.0.1' --port=8889 --policy=reject
```
```nginx
# Nginx config example
location / {
    proxy_pass http://127.0.0.1:8889;
    proxy_http_version 1.1;
    proxy_read_timeout 300;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Real-PORT $remote_port;
}
```

Running as a standalone server
```bash
wssh --port=8080 --sslport=4433 --certfile='cert.crt' --keyfile='cert.key' --xheaders=False --policy=reject
```


### Tips

* For whatever deployment choice you choose, don't forget to enable SSL.
* By default plain http requests from a public network will be either redirected or blocked and being redirected takes precedence over being blocked.
* Try to use reject policy as the missing host key policy along with your verified known_hosts, this will prevent man-in-the-middle attacks. The idea is that it checks the system host keys file("~/.ssh/known_hosts") and the application host keys file("./known_hosts") in order, if the ssh server's hostname is not found or the key is not matched, the connection will be aborted.
