import socketserver
import user
import command_parser
import command_handler

user.User.load_users()
print(user.User.users['zxc'].password)


class ServerHandler(socketserver.BaseRequestHandler):
    MAX_LENGTH = 1024
    MAX_CLIENT = 5
    NUM_CLIENT = 0

    def handle(self):

        # get the socket that connect to the client socket
        sock = self.request

        # check if number of clients is max
        if ServerHandler.NUM_CLIENT == ServerHandler.MAX_CLIENT:
            sock.send("Server overload!!!".encode())
            sock.close()
            return
        else:
            ServerHandler.NUM_CLIENT += 1
            sock.send(
                ("----------------Welcome to MySSH server----------------\n")
                .encode())

        # create user instance to process_command
        handler = command_handler.CommandHandler(
            None, command_parser.MyParser())

        # listen forever
        while not handler.stop:
            res = handler.process_request(sock.recv(self.MAX_LENGTH).decode())
            sock.send(res.encode())

        # close socket
        sock.close()


socketserver.ThreadingTCPServer(("", 12345), ServerHandler).serve_forever()
