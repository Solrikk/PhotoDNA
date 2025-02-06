import socket
import logging
from urllib.parse import urlparse

def get_ip_address(url):
    try:
        h = urlparse(url).hostname
        return socket.gethostbyname(h)
    except Exception as e:
        logging.warning(str(e))
        return None
