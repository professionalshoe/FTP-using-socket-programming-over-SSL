'''
FTP
functionalities-
    1)storing file in server (the files can be of any format)
    2)deleting file and folder in server
    3)getting a file from the server
    4)list the files on the server
    5)user authentication

future scope-
    1)transferring of folders
'''

import socket #socket programming
import ssl    #for secured socket progamming
import os     #for delting files and folder
import threading    #for multiclient 
import shutil       #for removing folder

# Server configuration
fixed_ip_of_server = "192.168.1.9"  # Server IP address
fixed_port_server = 9120  # Server port
fixed_server_folder_path = "./server_files"  # Directory path where server files are stored
ssl_key_file = "private.key"  # SSL key file
ssl_cert_file = "signedcert.pem"  # SSL certificate file
user_auth_file="userinfo.txt" #user info for login and signup

def authenticate_user(username, password):
    with open(user_auth_file, 'rb') as file:
        for line in file:
            stored_username, stored_password = line.decode("utf-8").strip().split()
            if username == stored_username and password == stored_password:
                return True
    return False

def register_user(username, password):
    with open(user_auth_file, 'ab') as file:
        file.write(f"{username} {password}\n".encode("utf-8"))

def handle_client_function(ssl_client_socket, addr):
    try:
        while True:
            # Receive and process client message
            message = ssl_client_socket.recv(1024).decode("utf-8")

            # Close client connection if requested
            if message.lower() == "close":
                ssl_client_socket.send("closed".encode("utf-8"))
                print(f"The socket {addr[0]}:{addr[1]} is successfully closed\n")
                break

            # Upload a file to the server
            elif message.lower() == "stor":
                file_exist = ssl_client_socket.recv(1024).decode("utf-8")

                # Handling cases of files existing or not
                if file_exist == "1":
                    # Receive file details
                    file_name = ssl_client_socket.recv(1024).decode("utf-8")
                    file_size = int(ssl_client_socket.recv(1024).decode("utf-8"))

                    # Open and write the file
                    file_name = os.path.join(fixed_server_folder_path, file_name)
                    with open(file_name, "wb") as file:
                        while file_size > 0:
                            data = ssl_client_socket.recv(1024)
                            file.write(data)
                            file_size -= len(data)
                        print(f"File transfer complete, stored in {file_name}\n")
                        ssl_client_socket.send("File transfer complete".encode("utf-8"))
                else:
                    ssl_client_socket.send("file doesn't exist".encode("utf-8"))
                    print("The file you want to upload doesn't exist\n")

            # List files on server
            elif message.lower() == "list":
                files = os.listdir(fixed_server_folder_path)
                if len(files) == 0:
                    ssl_client_socket.send("The server directory is empty".encode("utf-8"))
                    print("The server directory is empty\n")
                else:
                    ssl_client_socket.send("\n".join(f for f in files).encode("utf-8"))

            # Delete file on server
            elif message.lower() == "delete":
                file_name = ssl_client_socket.recv(1024).decode("utf-8")
                files = os.listdir(fixed_server_folder_path)
                if len(files) == 0:
                    ssl_client_socket.send("The server directory is empty".encode("utf-8"))
                    print("The server directory is empty\n")
                else:
                    if file_name in files:
                        file_path = os.path.join(fixed_server_folder_path, file_name)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            ssl_client_socket.send("File deleted successfully".encode("utf-8"))
                            print("File deleted successfully")
                        else:
                            shutil.rmtree(file_path)
                            ssl_client_socket.send("Folder deleted successfully".encode("utf-8"))
                            print("Folder deleted successfully")
                    else:
                        ssl_client_socket.send("File not found".encode("utf-8"))
                        print(f"File {file_name} not found\n")

            # Download file from server
            elif message.lower() == "get":
                file_name = ssl_client_socket.recv(1024).decode("utf-8")
                files = os.listdir(fixed_server_folder_path)
                if file_name not in files:
                    print(f"File {file_name} not found\n")
                    ssl_client_socket.send("File not found".encode("utf-8"))
                else:
                    ssl_client_socket.send("file found".encode("utf-8"))
                    file_path = os.path.join(fixed_server_folder_path, file_name)
                    file_size = os.path.getsize(file_path)
                    ssl_client_socket.send(str(file_size).encode("utf-8"))
                    with open(file_path, "rb") as f1:
                        while True:
                            data = f1.read(1024)
                            if not data:
                                break
                            ssl_client_socket.sendall(data)
                    print(f"File {file_name} successfully transferred\n")
                    ssl_client_socket.send(f"file {file_name} transferred successfully".encode("utf-8"))
            else:
                ssl_client_socket.send("Please enter a valid command".encode("utf-8"))

    except Exception as e:
        print(f"Error when handling client: {e}")

    finally:
        ssl_client_socket.close()
        print(f"Closed connection to client {addr[0]}:{addr[1]}\n")


def start_server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #IPV4 
        server_socket.bind((fixed_ip_of_server, fixed_port_server))
        server_socket.listen()
        print(f"Listening on server {fixed_ip_of_server}:{fixed_port_server}\n")

        while True:
            client_socket, client_addr_tuple = server_socket.accept()
            print(f"Accepted connection from {client_addr_tuple[0]}:{client_addr_tuple[1]}\n")

            # Create an SSL context
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=ssl_cert_file, keyfile=ssl_key_file)

            # Wrap the client socket with SSL
            ssl_client_socket = ssl_context.wrap_socket(client_socket, server_side=True)
            
            # Check if SSL connection is established
            cipher = ssl_client_socket.cipher()
            if cipher:
                print(f"SSL connection established using {cipher[0]} with encryption strength {cipher[2]}\n")

                # Start a new thread to handle the client
                existing_or_new_user=ssl_client_socket.recv(1024).decode("utf-8")
                if(existing_or_new_user=="existing"):
                    
                    username=ssl_client_socket.recv(1024).decode("utf-8")
                    passwd=ssl_client_socket.recv(1024).decode("utf-8")
                    if(authenticate_user(username,passwd)):
                        print(f"succesful login {username}\n")
                        ssl_client_socket.send("succesful login".encode("utf-8"))
                        thread = threading.Thread(target=handle_client_function, args=(ssl_client_socket, client_addr_tuple))
                        thread.start()
                    else:
                        ssl_client_socket.send("wrong credentials".encode("utf-8"))
                        ssl_client_socket.close()
                        print(f"Closed connection to client\n")

                elif(existing_or_new_user=="new"):
                    username=ssl_client_socket.recv(1024).decode("utf-8")
                    passwd=ssl_client_socket.recv(1024).decode("utf-8")
                    register_user(username,passwd)
                    ssl_client_socket.send("succesful register".encode("utf-8"))
                    thread = threading.Thread(target=handle_client_function, args=(ssl_client_socket, client_addr_tuple))
                    thread.start()
            else:
                print("The connection is not secure\n")

    except Exception as e:
        print(f"Error: {e}\n")

    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
