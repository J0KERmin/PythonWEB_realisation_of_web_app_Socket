from flask import Flask, render_template, request, send_from_directory, abort
import socket
import json
import os
import threading
from datetime import datetime
from threading import Thread

app = Flask(__name__)

# Serve static files
@app.route('/<path:path>')
def static_files(path):
    try:
        return send_from_directory('', path)
    except Exception:
        abort(404)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Message page
@app.route('/message.html')
def message():
    return render_template('message.html')

# Handle form submission
@app.route('/message', methods=['POST'])
def handle_message():
    username = request.form.get('username')
    message = request.form.get('message')

    # Send data to socket server
    send_to_socket_server(username, message)

    return "Message Sent!"

# Handle 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def send_to_socket_server(username, message):
    udp_ip = "127.0.0.1"
    udp_port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = json.dumps({"username": username, "message": message}).encode('utf-8')
    sock.sendto(data, (udp_ip, udp_port))

# Socket server function
def socket_server():
    udp_ip = "127.0.0.1"
    udp_port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))

    if not os.path.exists('storage'):
        os.makedirs('storage')

    # Перевірка існування файлу і створення, якщо не існує
    if not os.path.exists('storage/data.json'):
        with open('storage/data.json', 'w') as file:
            json.dump({}, file)

    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))
        timestamp = str(datetime.now())  # Час отримання повідомлення

        # Додання повідомлення у файл data.json
        with open('storage/data.json', 'r+') as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                json_data = {}

            # Додавання нового повідомлення з таймштампом як ключем
            json_data[timestamp] = message

            # Запис у файл
            file.seek(0)  # Початок файлу
            json.dump(json_data, file, indent=4)


# # Run the HTTP server and Socket server in parallel
# if __name__ == '__main__':
#     thread = threading.Thread(target=socket_server)
#     thread.start()

#     app.run(host='0.0.0.0', port=3000)

if __name__ == '__main__':
    # Запуск Flask-сервера в одному потоці
    flask_thread = Thread(target=app.run, kwargs={'port': 3000})
    flask_thread.start()

    # Запуск Socket-сервера в іншому потоці
    socket_thread = Thread(target=socket_server)
    socket_thread.start()