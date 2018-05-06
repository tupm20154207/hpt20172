import socketserver
import user
import command_parser
import command_handler


class ServerHandler(socketserver.BaseRequestHandler):
    MAX_LENGTH = 1024
    MAX_CLIENT = 5
    NUM_CLIENT = 0

    def handle_connect(self):
        # get the socket that connect to the client socket
        self.socket = self.request

        # check if number of clients is max
        if ServerHandler.NUM_CLIENT == ServerHandler.MAX_CLIENT:
            self.socket.send(bytes([0]) + "Server overloaded!".encode())
            self.socket.close()
            return None

        else:
            ServerHandler.NUM_CLIENT += 1
            self.socket.send(
                bytes([1]) +
                ("--------------Welcome to MySSH server-------------\n")
                .encode()
            )

        # create user instance to process commands
        self.handler = command_handler.CommandHandler(
            None, command_parser.MyParser())
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
                self.send_reply(seqno, cmd)

        except (ConnectionResetError, IndexError):
            if self.handler.user_ins is not None:
                self.handler.user_ins.log_out()

        finally:
            self.socket.close()


if __name__ == '__main__':

    user.User.load_users()
    socketserver.ThreadingTCPServer(("", 12345), ServerHandler).serve_forever()
    user.User.store_users()
