import socket
import select
import logging
# import logging.handlers
import fire


def open_sockets(host: str = None, ports: list = None):
    """
    :param host: str, default: None. IP address to bind to. If 'None', all addresses are used
    :param ports: list, default: None. List of desired ports
    :return: List of socket objects
    """
    if not ports:
        return list()
    sockets = list()
    for port in ports:
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                n_sock = socket.socket(af, socktype, proto)
            except Exception as e:
                continue
            try:
                n_sock.bind(sa)
                n_sock.listen(1)
            except Exception as e:
                n_sock.close()
                continue
            sockets.append(n_sock)
    return sockets


def write_to_file(line: str, file: str = "log.log"):
    """
    Simple file appender. Logging lib could be used
    :param line: str. What to append to file
    :param file: str, default: 'log.log'. File to append to
    :return: Nothing
    """
    with open(file, 'a+') as f:
        f.write(line)


def conf_log(file: str = 'log.log'):
    """
    Creates logger
    :param file:str. Flie to log to
    :return: logger
    """
    # hndlr = logging.handlers.TimedRotatingFileHandler(filename=file, backupCount=5, when='midnight', interval=24)
    hndlr = logging.FileHandler(filename=file, mode='a+')
    hndlr.setFormatter(logging.Formatter(fmt='%(asctime)s - %(message)s'))
    lggr = logging.getLogger('wh')
    lggr.addHandler(hndlr)
    lggr.setLevel(logging.INFO)
    return lggr


def run(host: str = None, ports: list = None, logfile: str = "log.log"):
    """
    Opens sockets for list of ports. Writes dest ip address to a file and closes connection
    :param host: str, default: None. IP address to bind to. If 'None', all addresses are used
    :param ports: list, default: None. List of desired ports
    :param logfile: str, default: 'log.log'. File to append to
    :return: Nothing
    """
    if not ports:
        print('no port to bind to')
        exit(1)
    lgr = conf_log(logfile)
    sockets = open_sockets(host, ports)
    if sockets:
        while True:
            active_sockets, _, _ = select.select(sockets, list(), list())
            for s in active_sockets:
                conn, addr = s.accept()
                lgr.info(addr[0])
                conn.close()


if __name__ == '__main__':
    fire.Fire(run)
