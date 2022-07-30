import mimetypes
import os.path
from uuid import uuid4

from wizardwebssh.settings import base_dir


def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files.
    Return (content_type, body) ready for httplib.HTTP instance
    """
    boundary = uuid4().hex
    CRLF = "\r\n"
    L = []
    for key, value in fields:
        L.extend(
            (
                f"--{boundary}",
                'Content-Disposition: form-data; name="%s"' % key,
                "",
                value,
            )
        )

    for key, filename, value in files:
        L.extend(
            (
                f"--{boundary}",
                'Content-Disposition: form-data; name="%s"; filename="%s"'
                % (key, filename),
                f"Content-Type: {get_content_type(filename)}",
                "",
                value,
            )
        )

    L.extend((f"--{boundary}--", ""))
    body = CRLF.join(L)
    content_type = f"multipart/form-data; boundary={boundary}"
    return content_type, body


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


def read_file(path, encoding="utf-8"):
    with open(path, "rb") as f:
        data = f.read()
        return data if encoding is None else data.decode(encoding)


def make_tests_data_path(filename):
    return os.path.join(base_dir, "tests", "data", filename)
