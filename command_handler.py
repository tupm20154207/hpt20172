import os
import user
import command_parser
import subprocess


class CommandHandler:
    def __init__(self, user_ins, parser):
        self.parser = parser
        self.set_user(user_ins)
        self.stop = False

    def set_user(self, user_ins):
        self.user_ins = user_ins

        if user_ins is not None:
            self.current_dir = os.path.abspath(user_ins.root_dir)
            self.root = '@' + self.user_ins.username + os.sep

    def process_request(self, command):

        succ, cmd, args, res = self.parser.parse(command)

        if succ:
            if cmd == 'login' or cmd == 'signup':
                if self.user_ins is not None:
                    res = "You must log out first.\n"
                else:
                    res = getattr(self, cmd)(args) +"\n"

            elif cmd != 'help' and self.user_ins is None:
                res = "You must login first.\n"

            else:
                res = getattr(self, cmd)(args) + "\n"

        return res

    def _exists(self, src, dst):
        """Check if src file or directory exists in dst location.
        Both src and dst path must be absolute"""

        src_name = src.split(os.sep)[-1]

        if os.path.isfile(src):
            items = [f for f in os.listdir(dst)
                     if os.path.isfile(dst + os.sep + f)]

        else:
            items = [f for f in os.listdir(dst)
                     if os.path.isdir(dst + os.sep + f)]

        for name in items:
            if src_name == name:
                return True

        return False

    def _get_abs(self, path):
        """Get the server's absolute path from the path specified by client"""

        path += os.sep

        if path.find('\\') != -1:
            path = path.replace('\\', os.sep)

        if path.find('/') != -1:
            path = path.replace('/', os.sep)

        if path.startswith(self.root):
            # The path is an absolute path
            abspath = os.path.abspath("users" + os.sep + path)

        elif path.startswith(".." + os.sep):
            """The path is an relative path starts from the proccess's parent
            directory"""
            if self.current_dir == os.path.abspath(self.user_ins.root_dir):
                # Prevent accessing root's parent directory
                return ""
            else:
                base = self.current_dir.split(os.sep)[:-1]
                rel = path.split(os.sep)[1:]
                abspath = os.sep.join(base + rel)

        elif path.startswith("." + os.sep):
            # The path is an relative path starts from current directory
            base = self.current_dir.split(os.sep)
            rel = path.split(os.sep)[1:]
            abspath = os.sep.join(base + rel)

        else:
            abspath = self.current_dir + os.sep + path

        # Filter out redundant separators
        abspath = os.sep.join(filter(None, abspath.split(os.sep)))

        return abspath

    def _get_parent(self, abspath):
        if abspath == os.path.abspath(self.user_ins.root_dir):
            return ""
        return os.sep.join(str(abspath).split(os.sep)[:-1])

    def _get_name(self, abspath):
        return abspath.split(os.sep)[-1]

    def login(self, arguments):
        res = ""
        username = arguments["USERNAME"]
        password = arguments["PASSWORD"]
        self.set_user(user.User.login(username, password))
        if self.user_ins is None:
            res = "Login failed!"
        else:
            res = "Login success!"
        return res

    def signup(self, arguments):
        res = ""
        username = arguments["USERNAME"]
        password = arguments["PASSWORD"]
        self.set_user(user.User.sign_up(username, password))
        if self.user_ins is None:
            res = "Sign up failed!"
        else:
            res = "Sign up success!"
        return res

    def logout(self, arguments):
        self.user_ins.log_out()
        self.user_ins = None
        return "See ya!"

    def cd(self, arguments):
        res = "done"
        dest = self._get_abs(arguments["DEST"])

        if os.path.isdir(dest):
            self.current_dir = dest

        else:
            res = "The system cannot find the path specified."

        return res

    def pwd(self, arguments):

        return self.current_dir[(self.current_dir + os.sep).find(self.root):]

    def date(self, arguments):
        res = ""

        if os.name == 'posix':
            res, _ = subprocess.Popen(
                ['date'], shell=True, stdout=subprocess.PIPE).communicate()
            res = res.decode()[:-1]

        elif os.name == 'nt':
            out1, _ = subprocess.Popen(
                ['date', '/T'],
                shell=True,
                stdout=subprocess.PIPE
            ).communicate()

            out2, _ = subprocess.Popen(
                ['time', '/T'],
                shell=True,
                stdout=subprocess.PIPE
            ).communicate()

            res = out1.decode()[:-2] + out2.decode()[:-2]

        else:
            res = "Service unavailable."

        return res

    def cp(self, arguments):
        """Allow copy if only the src path exists and the dst path is a
        directory"""

        src = self._get_abs(arguments["SOURCE"])
        dst = self._get_abs(arguments["DEST"])
        is_src_dir = arguments["directory"]

        res = "done."

        if os.path.exists(src) is False or\
                os.path.exists(dst) is False:

            res = "The system cannot find the path(s) specified."

        elif os.path.isfile(dst):
            res = "The destination path is a file."

        elif os.path.isdir(src) != is_src_dir:
            res = "Syntax error, try 'help cp' for more information."

        elif os.name != 'posix' and os.name != 'nt':
            res = "Service unavailable."

        elif os.path.isdir(src):
            if os.name == 'posix':
                subprocess.Popen(
                    ['cp', '-R', src, dst],
                    shell=True,
                ).communicate()

            else:
                src_name = src.split(os.sep)[-1]
                subprocess.Popen(
                    ['mkdir', src_name],
                    shell=True,
                    cwd=dst
                )

                subprocess.Popen(
                    ['xcopy', '/YE', src, dst + os.sep + src_name],
                    shell=True,
                ).communicate()
        else:
            if os.name == 'posix':
                subprocess.Popen(
                    ['cp', src, dst],
                    shell=True,
                ).communicate()
            else:
                subprocess.Popen(
                    ['copy', '/Y', src, dst],
                    shell=True,
                ).communicate()

        return res

    def mkdir(self, arguments):
        abs_dirs = [self._get_abs(x) for x in arguments['PATH']]
        valid_dirs = [dir for dir in abs_dirs
                      if os.path.isdir(self._get_parent(dir)) and
                      not os.path.isdir(dir)]

        res = "done."
        if len(valid_dirs) == 0:
            res = "The system cannot find the path(s) specified."
        else:
            subprocess.Popen(
                ['mkdir'] + valid_dirs,
                shell=True,
            ).communicate()
            res = "Success, invalid directories (if any) were discarded"

        return res

    def mv(self, arguments):
        src = self._get_abs(arguments["SOURCE"])
        dst = self._get_abs(arguments["DEST"])

        res = "done."

        if not os.path.exists(src) or\
                not os.path.exists(dst):
            res = "The system cannot find the path(s) specified."

        elif os.path.isfile(dst):
            res = "The destination path must be a directory"

        elif self._exists(src, dst):
            res = "Access denied: Name conflict occurs."

        elif os.name != 'posix' and os.name != 'nt':
            res = "Service unavailable."

        elif os.name == 'posix':
            subprocess.Popen(
                ['mv', src, dst],
                shell=True,
            ).communicate()

        else:
            subprocess.Popen(
                ['move', src, dst],
                shell=True,
            ).communicate()

        return res

    def ren(self, arguments):
        src = self._get_abs(arguments["SOURCE"])
        newname = arguments["NEWNAME"]
        parent = self._get_parent(src)
        res = "done"

        if not os.path.exists(src):
            res = "The system cannot find the path specified."

        elif parent == '':
            res = "Cannot rename root directory."

        elif os.name != 'posix' and os.name != 'nt':
            res = "Service unavailable."

        elif os.name == 'posix':
            subprocess.Popen(
                ['mv', self._get_name(src), newname],
                shell=True,
                cwd=parent
            ).communicate()

        else:
            subprocess.Popen(
                ['move', self._get_name(src), newname],
                shell=True,
                cwd=parent
            ).communicate()

        return res

    def rm(self, arguments):
        abspaths = [self._get_abs(x) for x in arguments['PATH']]
        isdir = arguments["directory"]
        res = "done."

        valid_paths = [path for path in abspaths
                       if os.path.exists(path) and
                       os.path.isdir(path) == isdir]

        if len(valid_paths) == 0:
            res = "The system cannot find the path(s) specified."

        elif os.name != 'posix' and os.name != 'nt':
            res = "Service unavailable."

        elif isdir:
            if os.name == 'posix':
                subprocess.Popen(
                    ['rm', '-rf'] + valid_paths,
                    shell=True,
                ).communicate()
            else:
                subprocess.Popen(
                    ['rd', '/S /Q'] + valid_paths,
                    shell=True,
                ).communicate()

            res = "Success, invalid arguments (if any) were discarded"

        else:
            if os.name == 'posix':
                subprocess.Popen(
                    ['rm', '-f'] + valid_paths,
                    shell=True,
                ).communicate()
            else:
                subprocess.Popen(
                    ['del', '/Q'] + valid_paths,
                    shell=True,
                ).communicate()

            res = "Success, invalid arguments (if any) were discarded"

        return res

    def echo(self, arguments):
        text = arguments['TEXT']
        file = arguments['file']
        res = ""

        if file is None:
            return ' '.join(text)

        file = self._get_abs(file)
        if not os.path.isdir(self._get_parent(file)) or \
                os.path.isdir(file):
            res = "File location invalid."

        elif os.name != 'posix' and os.name != 'nt':
            res = "Service unavailable."

        else:
            subprocess.Popen(
                ['echo', '>', file],
                shell=True,
            ).communicate()

        return res

    def ls(self, arguments):
        path = self._get_abs(arguments["PATH"])

        res = ""

        if not os.path.exists(path):
            res = "The system cannot find the path specified."

        elif os.name == 'posix':
            out, _ = subprocess.Popen(
                ['ls', '-al', '--full-time', path],
                shell=True,
                stdout=subprocess.PIPE
            ).communicate()

            arr = []

            if os.path.isfile(path):
                start = 1
            else:
                start = 0

            # Format the output
            for line in out.decode().split('\n')[start:]:
                if line != '':
                    line = line.split()
                    d =""
                    if line[0][0] == 'd':
                        d = '<DIR>'
                    arr.append('\t'.join([line[5], line[6][:5], d, line[4], line[8]])+'\n')

            res = ''.join(arr)

        elif os.name == 'nt':
            out, _ = subprocess.Popen(
                ['dir', path],
                shell=True,
                stdout=subprocess.PIPE
            ).communicate()
            res = '\n'.join(out.decode().split('\n')[4:-3])

        else:
            res = "Service unavailable."

        return res

    def quit(self, arguments):
        self.stop = True
        return self.logout()

    def help(self, arguments):
        cmd = arguments["COMMAND"]
        return self.parser.get_help(cmd)



