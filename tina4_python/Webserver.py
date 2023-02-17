#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from tina4_python.Constant import LOOKUP_HTTP_CODE
from tina4_python.Debug import Debug
from http.server import BaseHTTPRequestHandler
from tina4_python.Constant import *
from urllib.parse import urlparse, parse_qsl
import socket
import asyncio
import json


class Webserver:

    async def get_content_body(self):
        # get lines of content where at the end of the request
        content = self.request.split("\n\n")
        if len(content) == 2:
            content = content[1]

        try:
            content = json.loads(content)
        except Exception as e:
            content = ""

        return content

    async def get_response(self, method):
        params = dict(parse_qsl(urlparse(self.path).query, keep_blank_values=True))
        body = await self.get_content_body()
        request = {"params": params, "body": body, "raw": self.request}
        response = await self.router_handler.resolve(method, self.path, request, self.headers)

        headers = []
        self.send_header("Content-Type", response["content_type"], headers)
        self.send_header("Content-Length", str(len(response["content"])), headers)
        self.send_header("Connection", "Keep-Alive", headers)
        self.send_header("Keep-Alive", "timeout=5, max=30", headers)

        headers = await self.get_headers(headers, self.response_protocol, response["http_code"])
        if type(response["content"]) == str:
            return headers + response["content"].encode()
        else:
            return headers + response["content"]

    @staticmethod
    def send_header(header, value, headers):
        headers.append(header + ": " + value)

    @staticmethod
    async def get_headers(response_headers, response_protocol, response_code):
        headers = response_protocol + " " + str(response_code) + " " + LOOKUP_HTTP_CODE[
            response_code] + "\n"
        for header in response_headers:
            headers += header + "\n"
        headers += "\n"
        return headers.encode()

    async def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host_name, self.port))
        self.server_socket.listen(8)
        self.server_socket.setblocking(False)
        self.running = True

        loop = asyncio.get_event_loop()
        while True:
            client, _ = await loop.sock_accept(self.server_socket)
            loop.create_task(self.handle_client(client))

    async def handle_client(self, client):
        loop = asyncio.get_event_loop()
        request = None

        # Get the client request
        request = (await loop.sock_recv(client, 1024)).decode('utf8')
        # Decode the request

        self.request = request.replace("\r", "")

        self.path = request.split(" ")

        if len(self.path) > 1:
            self.path = self.request.split(" ")[1]

        self.method = self.request.split(" ")[0]

        initial = self.request.split("\n\n")[0]

        self.headers = initial.split("\n")

        method_list = [TINA4_GET, TINA4_ANY, TINA4_POST, TINA4_PATCH]

        contains_method = [ele for ele in method_list if (ele in self.method)]

        if self.method != "" and contains_method:
            response = await self.get_response(self.method)
            await loop.sock_sendall(client, response)

        client.close()

    def __init__(self, host_name, port):
        self.method = None
        self.response_protocol = "HTTP/1.1"
        self.headers = None
        self.response_headers = []
        self.request = None
        self.path = None
        self.server_socket = None
        self.host_name = host_name
        self.port = port
        self.router_handler = None
        self.running = False

    def serve_forever(self):
        asyncio.run(self.run_server())

    def server_close(self):
        self.running = False
        self.server_socket.close()
