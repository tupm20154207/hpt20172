import argparse
import shlex


class ParseError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        usage = self.format_usage()
        args = {'prog': self.prog, 'message': message}
        mess = ('%(prog)s: error: %(message)s\n') % args

        raise ParseError(usage + mess)


class CommandParser:

    def __init__(self):
        self.cd = ArgumentParser(
            prog="cd",
            description="Changes the current directory.",
            add_help=False
        )
        self.cp = ArgumentParser(
            prog="cp",
            description="Copies a file or directory to another location.",
            add_help=False
        )
        self.date = ArgumentParser(
            prog="date",
            description="Displays server current date time.",
            add_help=False
        )
        self.echo = ArgumentParser(
            prog="echo",
            description="Displays messages.",
            add_help=False
        )
        self.help = ArgumentParser(
            prog="help",
            description="Display help information for MySSH commands.",
            add_help=False
        )
        self.ls = ArgumentParser(
            prog="ls",
            description="Displays a list of files and subdirectories in a "
            "directory.",
            add_help=False
        )
        self.mkdir = ArgumentParser(
            prog="mkdir",
            description="Creates directories.",
            add_help=False
        )
        self.mv = ArgumentParser(
            prog="mv",
            description="Moves a file or directory to another directory.",
            add_help=False
        )
        self.pwd = ArgumentParser(
            prog="pwd",
            description="Displays the name of current directory",
            add_help=False
        )
        self.rm = ArgumentParser(
            prog="rm",
            description="Removes files or directories.",
            add_help=False
        )
        self.ren = ArgumentParser(
            prog="ren",
            description="Renames a file or directory.",
            add_help=False)
        self.quit = ArgumentParser(
            prog="quit",
            description="Quits MySSH program.",
            add_help=False
        )

        self.login = ArgumentParser(
            prog="login",
            description="Logins to MySSH server.",
            add_help=False
        )

        self.signup = ArgumentParser(
            prog="signup",
            description="Signs up a new account.",
            add_help=False
        )

        self.logout = ArgumentParser(
            prog="logout",
            description="Finishes current session.",
            add_help=False
        )

        self.cd.add_argument("DEST", help='Destination directory.')

        self.cp.add_argument("SOURCE", help='File/directory to be copied.')
        self.cp.add_argument("DEST", help='Destination directory.')
        self.cp.add_argument("-d", "--directory",
                             action='store_true',
                             help='Source path is a directory.')

        self.echo.add_argument("TEXT", nargs='*', help='Content to be echoed.')
        self.echo.add_argument('-f', '--file', help='Write TEXT to file.')

        self.help.add_argument(
            "COMMAND",
            nargs="?",
            choices=["cd", "cp", "date", "echo", "ls",
                     "mkdir", "mv", "pwd", "rm", "ren"],
            help='Command to display help information.'
        )

        self.ls.add_argument("PATH",
                             nargs="?",
                             default="",
                             help='List all files and directories in' +
                             'this path.')

        self.mkdir.add_argument("PATH", nargs="+", help='New directories.')

        self.mv.add_argument("SOURCE", help='Files/directories to be moved.')
        self.mv.add_argument("DEST", help='Destination directory.')

        self.rm.add_argument("-d", "--directory",
                             action="store_true",
                             help='PATH is a directory.')
        self.rm.add_argument("PATH",
                             nargs="+",
                             help='Files/directories to be removed.')

        self.ren.add_argument("SOURCE", help='Path to be renamed.')
        self.ren.add_argument("NEWNAME", help='New name.')

        self.login.add_argument("USERNAME", help='MySSH username.')
        self.login.add_argument("PASSWORD", help='Password.')

        self.signup.add_argument("USERNAME", help='MySSH username.')
        self.signup.add_argument("PASSWORD", help='Password.')

    def parse(self, string_command):
        mess = ""
        arguments = {}
        success = False
        command = ""
        args = shlex.split(string_command)

        try:
            command = args[0]
            cmd = getattr(self, command)
            arguments = vars(cmd.parse_args(args[1:]))
            success = True

        except ParseError as exc:
            mess = exc.message

        except AttributeError:
            mess = "Wrong command, try 'help' for more information\n"

        return success, command, arguments, mess

    def get_help(self, command):
        if command is None:
            res = ""
            cmds = list(self.__dict__.keys())
            cmds.sort()
            for cmd in cmds:
                res += cmd + '\t\t' + getattr(self, cmd).description + '\n'
            res += "\nFor more information on a specific command, " \
                "type 'help command-name'\n"

            return res

        return getattr(self, command).format_help()


if __name__ == '__main__':
    parser = CommandParser()
