from ftplib import FTP
from urllib.parse import urljoin

# TODO: Sacar todo esto a variables de entorno
USER = 't3user'
PASSWORD = 't3pass'
HOST = 'ftp.aleperno.com'
BASE_PATH = 'https://taller3.aleperno.com/storage/'

class FileStorage():
  def __init__(self, user=USER, password=PASSWORD, host=HOST):
    self.user = user
    self.password = password
    self.host = host

  def store(self, filename: str, file):
    ftp_connection = FTP(user=self.user, password=self.password, host=self.host)

    file.seek(0)
    ftp_connection.storbinary(f'STOR {filename}')

    ftp_connection.quit()
    return urljoin(BASE_PATH, filename)
  