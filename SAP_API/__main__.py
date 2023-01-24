import sys
import argparse
from SAP_API.API.Server import Server

def main():
    parser = argparse.ArgumentParser(description='Starts the SAP API Server')

    parser.add_argument("--host", "-s", type=str, default="127.0.0.1", help="Host to listen on")
    parser.add_argument("--port", "-p", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--whitelist", "-w", type=str, help="IPs to allow to connect to the server", action="append")
    parser.add_argument("--max-clients", "-m", type=int, default=32, help="Max number of clients to allow to connect to the server")
    parser.add_argument("--timeout", "-t", type=int, default=5, help="Timeout time in minutes")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable Debug Mode")

    args = parser.parse_args(sys.argv[1:])

    if(args.whitelist is None):
        args.whitelist = [args.host]

    print("Starting server on {}:{}".format(args.host, args.port))
    print("Whitelisted IPs: {}".format(args.whitelist))
    print("Max Clients: {}".format(args.max_clients))
    print("Timeout: {} minutes".format(args.timeout))
    print("Debug Mode: {}".format(args.debug))
    
    s = Server(host="127.0.0.1", port=5000, whitelist=["127.0.0.1"], maxClients=10, timeoutTime=5, debug=False)

if __name__ == "__main__":
    main()
