import threading
import time
import socket
from enum import Enum

class State(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class RaftConsensus:
    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port
        self.state = State.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.leader_id = "java1"  # Líder fijo para simplificar
        self.log = []
        self.peers = {}
        
    def start(self):
        print(f"{self.node_id} RAFT iniciado. Líder: {self.leader_id}")
        
        # Si somos Python workers, somos seguidores
        if self.node_id.startswith("python"):
            self.state = State.FOLLOWER
            
    def is_leader(self):
        return self.state == State.LEADER
    
    def get_leader_address(self):
        if self.leader_id == "java1":
            return "java-worker-1:5000"
        elif self.leader_id == "java2":
            return "java-worker-2:5001"
        elif self.leader_id == "python1":
            return "python-worker-1:5002"
        elif self.leader_id == "python2":
            return "python-worker-2:5003"
        return ""
    
    def get_state(self):
        return self.state.name
    
    def add_peer(self, peer_id, address):
        self.peers[peer_id] = address
        
    def replicate(self, data):
        # Simplificado
        print(f"Replicando: {data}")
        return True