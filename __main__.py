import sys
import argparse
from SAP_API.API.Server.Server import Server

import pickle

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Starts the SAP API Server')

    parser.add_argument("--host", "-s", type=str, default="127.0.0.1", help="Host to listen on")
    parser.add_argument("--port", "-p", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--whitelist", "-w", type=str, help="IPs to allow to connect to the server", action="append")
    parser.add_argument("--debug", "-d", help="Enable debug mode", action="store_true")

    args = parser.parse_args(sys.argv[1:])

    if(args.whitelist is None):
        args.whitelist = [args.host]

    print("Starting server on {}:{}".format(args.host, args.port))
    print("Whitelisted IPs: {}".format(args.whitelist))

    if(args.debug):
        print("DEBUG MODE ENABLED")

    s = Server(args.host, args.port, args.whitelist, args.debug)
    s.Start()
