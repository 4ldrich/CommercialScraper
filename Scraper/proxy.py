import socket



class Proxy():

    def __init__(self):
        hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(hostname)
        self.proxies = []



def main():
    proxy = Proxy()
    print(proxy.local_ip)


if __name__ == '__main__':
    main()