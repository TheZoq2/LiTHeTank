import json

def send_msg_to_socket(socket, msg):
    final_msg = "{}{}".format(len(msg), msg)

    socket.send(bytes(final_msg, 'utf-8'))

def decode_socket_data(server_data):
    data_chunks = []
    while (server_data):
        index = server_data.find('{')
        bytes_to_read = int(server_data[0:index])
        server_data = server_data[index:]
        data_chunks.append(server_data[0:bytes_to_read])
        server_data = server_data[bytes_to_read:]
    return data_chunks

def create_socket_msg(type, payload):
    return json.dumps({"type": type, "data": payload},)

