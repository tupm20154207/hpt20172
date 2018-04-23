import socket
import sys


class OverloadException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


if __name__ == '__main__':

    host = socket.gethostname()
    port = 12345

    try:
        if len(sys.argv) > 1:
            host = sys.argv[1]
        if len(sys.argv) > 2:
            port = int(sys.argv[2])

        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))

        greeting = s.recv(4096).decode()

        if greeting == "Server overload!!!":
            raise OverloadException("Server overload!!!")

        sys.stdout.write(greeting + '\n')

        while True:
            inp = ""
            while inp == "":
                inp = input("$ ")
            s.send(inp.encode())
            sys.stdout.write(s.recv(4096).decode() + '\n')

    except ValueError:
        sys.stderr.write("Error: Port number must be an integer!!")
        sys.exit(1)

    except TimeoutError:
        sys.stderr.write("Time out!!")
        sys.exit(1)

    except OverloadException as e:
        sys.stdout.write(e.message)
        sys.exit(1)
