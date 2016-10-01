
def decode_server_data(server_data):
    data_chunks = []
    while (server_data):
        index = server_data.find('{')
        bytes_to_read = int(server_data[0:index])
        server_data = server_data[index:]
        data_chunks.append(server_data[0:bytes_to_read])
        server_data = server_data[bytes_to_read:]
    return data_chunks
