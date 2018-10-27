from argparse import ArgumentParser

from client.client import Client
from server.server import Server


def main():
    """ Creates a Server and Client and starts the Chat Room """
    #
    parser = ArgumentParser()
    parser.add_argument(
        "-ip",
        "--IPAddress",
        help="Please provide your "
    )


if __name__ == '__main__':
    main()