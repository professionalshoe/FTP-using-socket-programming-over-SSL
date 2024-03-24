import socket
import ssl
import os

# Client configuration
fixed_ip_of_server = "192.168.1.9"
fixed_port_server = 9120
fixed_client_folder_path = "./client_files"
ssl_cert_file = "signedcert.pem"

def run_client():
    try:
        # Create an SSL context
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.check_hostname = False  # Disable hostname verification
        ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification

        # Create a TCP socket
        client = socket.create_connection((fixed_ip_of_server, fixed_port_server))

        # Wrap the TCP socket with SSL
        ssl_client_socket = ssl_context.wrap_socket(client, server_hostname=fixed_ip_of_server)

        new_or_existing_user=input("existing or new user: ")
        ssl_client_socket.send(new_or_existing_user.encode("utf-8"))
        
        username=input("username: ")
        passwd=input("passwd: ")
        ssl_client_socket.send(username.encode("utf-8"))
        ssl_client_socket.send(passwd.encode("utf-8"))
        user_auth=ssl_client_socket.recv(1024).decode("utf-8")
        print(f"{user_auth}")
        if(user_auth=="wrong credentials"):
            ssl_client_socket.close()
            exit(0)

        while True:
            # Get user input for the action to perform
            msg = input("\nWhat do you want to do?\nSTOR - Upload a file\nLIST - See files on server\nDELETE - Delete a file\nGET - Get a file from server\nCLOSE - Close the connection\n")

            # Send the user input to the server
            ssl_client_socket.send(msg.encode("utf-8"))

            if msg.lower() == "stor":  # Upload a file to the server
                file_name = input("Enter file name: ")
                file_path = os.path.join(fixed_client_folder_path, file_name)

                if os.path.exists(file_path):
                    ssl_client_socket.send("1".encode("utf-8"))  # Indicate file exists
                    file_size = os.path.getsize(file_path)

                    # Send file name and size to the server
                    ssl_client_socket.send(file_name.encode("utf-8"))
                    ssl_client_socket.send(str(file_size).encode("utf-8"))

                    # Send the file content to the server
                    with open(file_path, "rb") as file:
                        while file_size > 0:
                            data = file.read(1024)
                            ssl_client_socket.send(data)
                            file_size -= len(data)
                    print("File transfer complete")
                else:
                    ssl_client_socket.send("0".encode("utf-8"))  # Indicate file does not exist

            elif msg.lower() == "delete":  # Delete a file on the server
                file_name = input("File/folder name: ")
                ssl_client_socket.send(file_name.encode("utf-8"))

            elif msg.lower() == "get":  # Download a file from the server
                file_name = input("File name: ")
                ssl_client_socket.send(file_name.encode("utf-8"))

            # Receive response from the server
            response_from_server = ssl_client_socket.recv(1024).decode("utf-8")

            if response_from_server.lower() == "file found":  # File found on server
                file_path = os.path.join(fixed_client_folder_path, file_name)
                file_size = int(ssl_client_socket.recv(1024).decode("utf-8"))
                received_size = 0

                # Receive and write file content
                with open(file_path, "wb") as file:
                    while received_size < file_size:
                        data = ssl_client_socket.recv(1024)
                        received_size += len(data)
                        file.write(data)
                response_from_server = ssl_client_socket.recv(1024).decode("utf-8")

            if response_from_server.lower() == "closed":  # Server closed the connection
                break  

            print(f"Received: {response_from_server}")  # Print server response

    except Exception as e:
        print(f"Error: {e}")

    finally:
        ssl_client_socket.close()  # Close the SSL socket
        print("Connection to server closed")  # Print connection closed message


if __name__ == "__main__":
    run_client()
