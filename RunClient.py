from SAP_API.API.Client.Client import Client

if __name__ == "__main__":
    c = Client("127.0.0.1", 5000)
    state = c.GetGameState()