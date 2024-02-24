from ftplib import FTP, all_errors
from urllib.parse import urljoin
import os


USER = os.environ.get('FTPUSER', 'XXX')
PASSWORD = os.environ.get('FTPPASS', 'XXX')
HOST = os.environ.get('FTPHOST', 'XXX')
BASE_PATH = os.environ.get('FTPPATH', 'XXXX')


class StorageError(Exception):
    pass


class NotConnectedError(Exception):
    pass


def retry(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except NotConnectedError:
            raise
        except Exception as e:
            self._connect()
            return func(self, *args, **kwargs)

    return wrapper


class StorageHandler(object):

    def __init__(self, user=USER, password=PASSWORD, host=HOST):
        self.user = user
        self.password = password
        self.host = host
        self.ftp = None

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.ftp:
            self.ftp.quit()

    def _connect(self):
        try:
            self.ftp = FTP(host=self.host, user=self.user, passwd=self.password)
        except Exception as e:
            raise StorageError(e)

    @retry
    def list_files(self):
        if not self.ftp:
            raise NotConnectedError("Not connected to FTP server")
        return set(self.ftp.nlst())

    @retry
    def exists(self, filename):
        if not self.ftp:
            raise NotConnectedError("Not connected to FTP server")
        return filename in self.list_files()

    @retry
    def upload(self, filename, bytesio):
        if not self.ftp:
            raise NotConnectedError("Not connected to FTP server")
        bytesio.seek(0)
        self.ftp.storbinary(f'STOR {filename}', bytesio)
        return urljoin(BASE_PATH, filename)

    @retry
    def download(self, filename, callback):
        if not self.ftp:
            raise NotConnectedError("Not connected to FTP server")
        self.ftp.retrbinary(f'RETR {filename}', callback)

    @retry
    def delete(self, filename):
        if not self.ftp:
            raise NotConnectedError("Not connected to FTP server")
        self.ftp.delete(filename)
