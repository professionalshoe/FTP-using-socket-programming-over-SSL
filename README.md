# FTP using socket programming over SSL
Client server model with multiple clients and one server and file transfer between them

STEPS:

1. Run the SERVER program
2. Run the CLIENT program in another terminal on the same system/or different system(if appropiate certificates generated and added to user certificates)
3. The clients entering the server specify if they are existing users(type existing) or new users(type new) and provider appropiate user name and password for the same
4. the login/signup is crosschecked by the server using userinfo.txt file and connection is accepted or rejected appropiately
5. Multiple CLIENTS can join the same SERVER and share files to and from server
6. Each client has the following options (LIST-to see current server files,STOR-to upload a file to server,
   GET-to get a file from the server, DELETE- to delete a file from the server, CLOSE- to gracefully exit the connection)
8. Mechanism to check if ssl is working or not
9. Ensure the existence of "server_files" and "client_files" directory in the same directory as client code and server code in the
    server and client systems respectively


The program is configured to use a signed certificate and a private key to implement ssl. 
Generate the necessary certificate and files
Ensure the naming of the files before running the program

Steps to generate a self signed certificate

1. openssl genrsa -aes256 -out private.key 2048
2. openssl rsa -in private.key -out private.key
3. openssl req -new -x509 -nodes -sha1 -key private.key -out certificate.crt -days 36500 -addext "subjectAltName=IP:<SERVER HOST IPV4>"
4. openssl req -x509 -new -nodes -key private.key -sha1 -days 36500 -out signedcert.pem -addext "subjectAltName=IP:<SERVER HOST IPV4>" 

Choose the desired length of the rsa key you want to generate. 4098 or 2048 or whatever
Choose the validity of the certificate. here we do so in days
Enter the IPV4 address on which the server is to run
Add the certificate.crt file generate onto the Trusted Root Certification Authorities\Certificates directory
The server requires the .pem and the .key files both
The client requires the .pem file
Ensure they are in the same directories as the server and client programs
Alternatively modify client ans server programs to reflect the locations of the .key and .pem files

REFERENCES:

1. socket programming in python
https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python

3. SSL implementation
https://www.youtube.com/watch?v=N4utwloVeOE
