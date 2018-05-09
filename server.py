import socketserver
import user
import command_parser
import command_handler
import sys
import time


class OverloadException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ServerHandler(socketserver.BaseRequestHandler):
    MAX_LENGTH = 1024
    MAX_CLIENT = 2
    NUM_CLIENT = 0

    def handle_connect(self):
        # get the socket that connect to the client socket
        self.socket = self.request

        # check if number of clients is max
        if ServerHandler.NUM_CLIENT == ServerHandler.MAX_CLIENT:
            self.socket.send(bytes([0]) + "Server overloaded!".encode())
            raise OverloadException()

        else:
            ServerHandler.NUM_CLIENT += 1
            self.socket.send(
                bytes([1]) +
                ("--------------Welcome to MySSH server-------------\n")
                .encode()
            )

        # create user instance to process commands
        self.handler = command_handler.CommandHandler(
            None, command_parser.CommandParser())
        self.ackno = 0
        self.record = {}

    def get_request(self):
        req = self.socket.recv(self.MAX_LENGTH)
        return req[0], req[1:].decode()

    def do_operation(self, command):
        self.ackno = (self.ackno + 1) % 256

        res = self.handler.process_request(command)

        # Flush all records in memory when it's full
        if self.ackno == 0:
            self.record.clear()

        # Save result for retransmission
        self.record[self.ackno] = res

        return res

    def send_reply(self, seqno, command):
        if seqno == (self.ackno + 1) % 256:
            res = self.do_operation(command)
        elif self.record.get(seqno) is not None:
            res = self.record.get(seqno)
        else:
            res = 'Failed to process current request!'

        self.socket.send(bytes([seqno]) + res.encode())

    def handle(self):

        try:
            self.handle_connect()

            # listen until client type 'quit'
            while not self.handler.stop:
                seqno, cmd = self.get_request()
                # time.sleep(6)
                self.send_reply(seqno, cmd)

            ServerHandler.NUM_CLIENT -= 1

        except (ConnectionResetError, IndexError):
            if self.handler.user_ins is not None:
                self.handler.user_ins.log_out()

            ServerHandler.NUM_CLIENT -= 1

        except OverloadException:
            pass

        finally:
            self.socket.close()


if __name__ == '__main__':
    host = ""
    port = 12345

    try:
        if len(sys.argv) > 1:
            host = sys.argv[1]
        if len(sys.argv) > 2:
            port = int(sys.argv[2])

        user.User.load_users()
        socketserver.ThreadingTCPServer(
            (host, port), ServerHandler).serve_forever()
        user.User.store_users()

    except ValueError:
        sys.stderr.write("Error: Port number must be an integer!!")
        sys.exit(1)
