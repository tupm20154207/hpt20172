import socket
import sys


class SshClient:
    def __init__(self):
        self.MAX_RECEIVE = 4096
        self.socket = socket.socket()
        self.socket.settimeout(3)
        self.seqno = 0
        self.ackno = 0

    def connect(self, address, port):
        try:
            self.socket.connect((address, port))
            mess = self.socket.recv(self.MAX_RECEIVE)
            if mess[0] == 0:
                sys.stderr.write(mess[1:].decode())
                exit(1)
            else:
                sys.stdout.write(mess[1:].decode())

        except socket.error:
            sys.stderr.write('Unable to locate MySsh server!')
            exit(1)

    def request(self, command, seqno, count=0):
        try:
            if count == 3:
                raise socket.error

            self.socket.send(bytes([seqno]) + command.encode())
            while True:
                res = self.socket.recv(self.MAX_RECEIVE)
                if res[0] == (self.ackno + 1) % 256:
                    self.ackno = (self.ackno + 1) % 256
                    sys.stdout.write(res[1:].decode())
                    break

        except socket.timeout as e1:
            sys.stderr.write(
                'Retransmit:\n Seq#:{0}\nMessage:{1}\n'.format(seqno, command))
            self.request(command, seqno, count + 1)

        except socket.error as e2:
            sys.stderr.write('Server currently unavailable!')
            exit(1)

        except ConnectionAbortedError as e3:
            exit(0)

    def communicate(self):
        while True:
            cmd = input('$ ')
            if cmd.strip() == '':
                continue
            self.seqno = (self.seqno + 1) % 256
            self.request(cmd, self.seqno)
            if cmd == 'quit':
                break


if __name__ == '__main__':

    host = socket.gethostname()
    port = 12345

    try:
        if len(sys.argv) > 1:
            host = sys.argv[1]
        if len(sys.argv) > 2:
            port = int(sys.argv[2])

        client = SshClient()
        client.connect(host, port)
        client.communicate()

    except ValueError:
        sys.stderr.write("Error: Port number must be an integer!!")
        sys.exit(1)
