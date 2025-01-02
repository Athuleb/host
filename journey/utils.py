import socket
def is_internet_available():
    try:
        # Try connecting to a public DNS server (e.g., Google's DNS).
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False