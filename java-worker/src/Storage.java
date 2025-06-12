import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;

public class Storage {
    private String workerId;
    private Map<String, MLModel> models;
    private List<String> logs;
    
    public Storage(String workerId) {
        this.workerId = workerId;
        this.models = new ConcurrentHashMap<>();
        this.logs = new ArrayList<>();
    }
    
    public void saveModel(String modelId, MLModel model) {
        models.put(modelId, model);
        log("Model saved: " + modelId);
    }
    
    public MLModel loadModel(String modelId) {
        return models.get(modelId);
    }
    
    public int getModelCount() {
        return models.size();
    }
    
    public String getRecentLogs() {
        StringBuilder sb = new StringBuilder();
        int start = Math.max(0, logs.size() - 10);
        for (int i = start; i < logs.size(); i++) {
            sb.append(logs.get(i)).append("\n");
        }
        return sb.toString();
    }
    
    private void log(String message) {
        String timestamp = java.time.LocalDateTime.now().toString();
        logs.add(timestamp + ": " + message);
        if (logs.size() > 100) {
            logs.remove(0);
        }
    }
}