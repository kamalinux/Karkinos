from flask import Flask, render_template, request

import os
import time
import struct
import socket
import threading
app = Flask(__name__)

wsgi_app = app.wsgi_app

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Server not running')
    func()

def startListen():
    global client_address, client_socket, s
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    client_socket, client_address = s.accept()

    return client_socket

def getData(client_socket):
    #client_socket.setblocking(0)
    client_socket.settimeout(0.5)
    data = bytearray()
    try:
        while 1:
            packet = client_socket.recv(BUFFER_SIZE)
            #print(packet)
            data.extend(packet)
    except socket.timeout as e:
        print(data)
        return data.decode()

    return data.decode()

def shell(c):
    global thread, client_socket, s
    command = c + "\n"
    client_socket.send(command.encode())

    return True

@app.route('/config', methods = ['POST'])
def config():
    global SERVER_PORT, connected
    SERVER_PORT = int(request.form['port'])
    print(SERVER_PORT)
    if connected == False:
        tmpsock = startListen()
        out = getData(tmpsock)
        connected = True
    return render_template('index.html', out=out)

@app.route('/', methods = ['POST', 'GET'])
def index():
    global out, client_socket
    if request.method == "POST":
        c = request.form['command']
        shell(c)
        out += getData(client_socket)
        out += "\n\n"
    return render_template('index.html', out=out)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5011
    BUFFER_SIZE = 1024
    client_socket = ""
    client_address = ""
    out = ""
    connected = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(SERVER_HOST, PORT)
    
