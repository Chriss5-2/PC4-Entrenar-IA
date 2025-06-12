from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class HttpMonitor:
    def __init__(self, port, worker):
        self.port = port
        self.worker = worker
        
    def start(self):
        try:
            server = HTTPServer(('0.0.0.0', self.port), self.create_handler())
            print(f"Monitor HTTP iniciado en puerto {self.port}")
            server.serve_forever()
        except Exception as e:
            print(f"Error iniciando monitor HTTP: {e}")
    
    def create_handler(self):
        worker = self.worker
        
        class StatusHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    html = f"""
                    <html>
                    <head>
                        <title>Worker Monitor</title>
                        <meta http-equiv='refresh' content='5'>
                    </head>
                    <body>
                        <h1>Worker Status</h1>
                        <p>Worker ID: {worker.worker_id}</p>
                        <p>RAFT State: {worker.raft.get_state()}</p>
                        <p>Leader: {worker.raft.leader_id}</p>
                        <p>Models: {worker.storage.get_model_count()}</p>
                        <h2>Recent Logs</h2>
                        <pre>{worker.storage.get_recent_logs()}</pre>
                    </body>
                    </html>
                    """
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html.encode())
                except Exception as e:
                    print(f"Error en monitor: {e}")
            
            def log_message(self, format, *args):
                return
                
        return StatusHandler