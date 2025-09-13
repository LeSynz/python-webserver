from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json

def load_todos():
    with open("todos.json", "r") as f:
        data = json.load(f)
        return data

def save_todos(todos):
    with open("todos.json", "w") as f:
        json.dump(todos, f)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        todos = load_todos()

        if path == "/todos":

            task_id = query.get("id", [None])[0]
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            if task_id:
                try:
                    task_id = int(task_id)
                    matched_task = next((todo for todo in todos if todo["id"] == task_id), None)
                    if matched_task:
                        self.wfile.write(json.dumps(matched_task).encode())
                    else:
                        self.send_response(404)
                        self.wfile.write(json.dumps({"error": "Task not found"}).encode())
                except ValueError:
                    self.send_response(400)
                    self.wfile.write(json.dumps({"error": "Invalid ID"}).encode())
            else:
                self.wfile.write(json.dumps(todos).encode())
    
    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/todos":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            # parse json or smt
            try:
                data = json.loads(body)
                title = data.get("title")
                if not title:
                    raise ValueError("Missing 'title")
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                return
            
            # load exisiting tooodso
            todos = load_todos()
            new_id = (max((todo["id"] for todo in todos), default=0) + 1)
            new_task = {"id": new_id, "title": title}
            todos.append(new_task)

            save_todos(todos)

            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(new_task).encode())

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/todos":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            #parse json
            try:
                data = json.loads(body)
                id = data.get("id")
                if not id:
                    raise ValueError('Missing value "id"')
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                return
            
            # load todos
            todos = load_todos()
            # todos["id"].remove(id)
            removed_id = next((todo for todo in todos if todo["id"] == id), None)

            if removed_id is None:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "ID not found or doesn't exist"}).encode())
                return

            todos.remove(removed_id)

            save_todos(todos)

            self.send_response(200)

server = HTTPServer(("localhost", 3000), Handler)
print('Server started at http://localhost:3000/')
server.serve_forever()