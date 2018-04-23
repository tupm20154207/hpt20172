import argparse
import os
def command_parser(args):
    parser = argparse.ArgumentParser()
    return parser.parse_args(args=args)


if __name__ == '__main__':
    command_parser('-h')
    os.system()
