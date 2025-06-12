import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;  // <-- Agregar este import
import java.net.*;
import java.io.*;

public class RaftConsensus {
    enum State { FOLLOWER, CANDIDATE, LEADER }
    
    private String nodeId;
    private State state = State.FOLLOWER;
    private int currentTerm = 0;
    private String votedFor = null;
    private String leaderId = null;
    private List<LogEntry> log = new CopyOnWriteArrayList<>();
    private Map<String, Peer> peers = new ConcurrentHashMap<>();
    private ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(3);
    private int port;
    private long lastHeartbeat = System.currentTimeMillis();
    private ServerSocket raftSocket;
    private volatile boolean running = true;
    
    class Peer {
        String id;
        String host;
        int port;
        
        Peer(String id, String host, int port) {
            this.id = id;
            this.host = host;
            this.port = port;
        }
    }
    
    public RaftConsensus(String nodeId, int port) {
        this.nodeId = nodeId;
        this.port = port;
    }
    
    public void start() {
        try {
            // Para simplificar, hacer que java1 sea siempre el líder inicial
            if (nodeId.equals("java1")) {
                becomeLeader();
            } else {
                leaderId = "java1";
                state = State.FOLLOWER;
            }
            
            // Servidor RAFT en puerto base + 1000
            raftSocket = new ServerSocket(port + 1000);
            System.out.println(nodeId + " RAFT iniciado en puerto " + (port + 1000));
            
            // Thread para manejar mensajes RAFT
            new Thread(() -> {
                while (running) {
                    try {
                        Socket peer = raftSocket.accept();
                        new Thread(() -> handleRaftMessage(peer)).start();
                    } catch (Exception e) {
                        if (running) {
                            e.printStackTrace();
                        }
                    }
                }
            }).start();
            
            // Solo iniciar timeout de elección si no somos el líder inicial
            if (!nodeId.equals("java1")) {
                startElectionTimeout();
            }
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private void startElectionTimeout() {
        scheduler.schedule(() -> {
            if (state != State.LEADER && 
                System.currentTimeMillis() - lastHeartbeat > 5000) { // 5 segundos timeout
                startElection();
            }
            if (state != State.LEADER) {
                startElectionTimeout();
            }
        }, 5000, TimeUnit.MILLISECONDS);
    }
    
    private synchronized void startElection() {
        // Solo iniciar elección si perdimos contacto con el líder
        if (leaderId != null && System.currentTimeMillis() - lastHeartbeat < 5000) {
            return;
        }
        
        state = State.CANDIDATE;
        currentTerm++;
        votedFor = nodeId;
        leaderId = null;
        
        System.out.println(nodeId + " iniciando elección para término " + currentTerm);
        
        int votesNeeded = (peers.size() + 1) / 2 + 1;
        AtomicInteger votes = new AtomicInteger(1); // Voto por sí mismo
        
        CountDownLatch latch = new CountDownLatch(peers.size());
        
        for (Peer peer : peers.values()) {
            CompletableFuture.runAsync(() -> {
                if (requestVote(peer, currentTerm)) {
                    votes.incrementAndGet();
                }
                latch.countDown();
            });
        }
        
        try {
            latch.await(2, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        if (votes.get() >= votesNeeded && state == State.CANDIDATE) {
            becomeLeader();
        } else {
            state = State.FOLLOWER;
            startElectionTimeout();
        }
    }
    
    private boolean requestVote(Peer peer, int term) {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(peer.host, peer.port + 1000), 1000);
            
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            
            out.println("VOTE_REQUEST|" + nodeId + "|" + term);
            String response = in.readLine();
            
            return response != null && response.equals("VOTE_GRANTED");
        } catch (Exception e) {
            return false;
        }
    }
    
    private synchronized void becomeLeader() {
        state = State.LEADER;
        leaderId = nodeId;
        System.out.println(nodeId + " es ahora el LÍDER del término " + currentTerm);
        
        // Iniciar heartbeats
        sendHeartbeats();
    }
    
    private void sendHeartbeats() {
        scheduler.scheduleAtFixedRate(() -> {
            if (state == State.LEADER) {
                for (Peer peer : peers.values()) {
                    sendHeartbeat(peer);
                }
            }
        }, 0, 1000, TimeUnit.MILLISECONDS); // Heartbeat cada segundo
    }
    
    private void sendHeartbeat(Peer peer) {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(peer.host, peer.port + 1000), 500);
            
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            out.println("HEARTBEAT|" + nodeId + "|" + currentTerm);
        } catch (Exception e) {
            // Ignorar errores de conexión
        }
    }
    
    private void handleRaftMessage(Socket socket) {
        try {
            BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            
            String message = in.readLine();
            if (message == null) {
                socket.close();
                return;
            }
            
            String[] parts = message.split("\\|");
            String messageType = parts[0];
            
            switch (messageType) {
                case "HEARTBEAT":
                    handleHeartbeat(parts, out);
                    break;
                case "VOTE_REQUEST":
                    handleVoteRequest(parts, out);
                    break;
            }
            
            socket.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private synchronized void handleHeartbeat(String[] parts, PrintWriter out) {
        if (parts.length >= 3) {
            String senderId = parts[1];
            int term = Integer.parseInt(parts[2]);
            
            if (term >= currentTerm) {
                currentTerm = term;
                state = State.FOLLOWER;
                leaderId = senderId;
                lastHeartbeat = System.currentTimeMillis();
                votedFor = null;
            }
            
            out.println("OK");
        }
    }
    
    private synchronized void handleVoteRequest(String[] parts, PrintWriter out) {
        if (parts.length >= 3) {
            String candidateId = parts[1];
            int term = Integer.parseInt(parts[2]);
            
            if (term > currentTerm) {
                currentTerm = term;
                votedFor = null;
                state = State.FOLLOWER;
            }
            
            if (term == currentTerm && (votedFor == null || votedFor.equals(candidateId))) {
                votedFor = candidateId;
                out.println("VOTE_GRANTED");
            } else {
                out.println("VOTE_DENIED");
            }
        }
    }
    
    public void replicate(String data) {
        if (state != State.LEADER) {
            return;
        }
        
        LogEntry entry = new LogEntry(currentTerm, data);
        log.add(entry);
        
        // Replicar a seguidores
        for (Peer peer : peers.values()) {
            CompletableFuture.runAsync(() -> replicateToFollower(peer, data));
        }
    }
    
    private void replicateToFollower(Peer peer, String data) {
        try (Socket socket = new Socket(peer.host, peer.port)) {
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            out.println("REPLICATE|" + data);
        } catch (Exception e) {
            // Ignorar errores
        }
    }
    
    public boolean isLeader() {
        return state == State.LEADER;
    }
    
    public String getLeaderId() {
        return leaderId;
    }
    
    public String getLeaderAddress() {
        if (leaderId == null) return null;
        
        if (leaderId.equals(nodeId)) {
            return "localhost:" + port;
        }
        
        Peer leader = peers.get(leaderId);
        if (leader != null) {
            return leader.host + ":" + leader.port;
        }
        
        // Fallback
        if (leaderId.equals("java1")) return "java-worker-1:5000";
        if (leaderId.equals("java2")) return "java-worker-2:5001";
        if (leaderId.equals("python1")) return "python-worker-1:5002";
        if (leaderId.equals("python2")) return "python-worker-2:5003";
        
        return null;
    }
    
    public String getState() {
        return state.toString();
    }
    
    public void addPeer(String peerId, String host, int port) {
        peers.put(peerId, new Peer(peerId, host, port));
    }
    
    class LogEntry {
        int term;
        String data;
        
        LogEntry(int term, String data) {
            this.term = term;
            this.data = data;
        }
    }
}