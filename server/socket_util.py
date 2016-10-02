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


def decode_socket_json_msg(msg):
    loaded_data = json.loads(msg)

    type = loaded_data["type"]
    
    data = {}
    if loaded_data["data"] != "":
        data = json.loads(loaded_data["data"])

    return (type, data)


class SocketBuffer:
    def __init__(self):
        self.buffer = ""

    def push_string(self, str):
        self.buffer += str

    def get_messages(self):
        result = []

        running = True
        while running:
            if(self.buffer.find("{")):
                index = self.buffer.find("{")
                bytes_to_read = int(self.buffer[0:index])

                if len(self.buffer) > bytes_to_read + index:
                    self.buffer = self.buffer[index:]
                    result.append(self.buffer[0:bytes_to_read])
                    self.buffer = self.buffer[bytes_to_read:]
            else:
                running = False

        return  result

