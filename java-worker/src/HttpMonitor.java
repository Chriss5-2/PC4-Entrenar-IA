import com.sun.net.httpserver.*;
import java.net.InetSocketAddress;
import java.io.OutputStream;
import java.io.IOException;

public class HttpMonitor {
    private HttpServer server;
    private Worker worker;
    
    public HttpMonitor(int port, Worker worker) {
        this.worker = worker;
        try {
            server = HttpServer.create(new InetSocketAddress(port), 0);
            server.createContext("/", new StatusHandler());
            server.setExecutor(null);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void start() {
        server.start();
    }
    
    class StatusHandler implements HttpHandler {
        public void handle(HttpExchange exchange) throws IOException {
            String response = generateStatusPage();
            exchange.sendResponseHeaders(200, response.length());
            OutputStream os = exchange.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
        
        private String generateStatusPage() {
            StringBuilder html = new StringBuilder();
            html.append("<html><head><title>Worker Monitor</title>");
            html.append("<meta http-equiv='refresh' content='5'></head>");
            html.append("<body><h1>Worker Status</h1>");
            html.append("<p>Worker ID: ").append(worker.workerId).append("</p>");
            html.append("<p>RAFT State: ").append(worker.raft.getState()).append("</p>");
            html.append("<p>Models: ").append(worker.storage.getModelCount()).append("</p>");
            html.append("<h2>Recent Logs</h2>");
            html.append("<pre>").append(worker.storage.getRecentLogs()).append("</pre>");
            html.append("</body></html>");
            return html.toString();
        }
    }
}