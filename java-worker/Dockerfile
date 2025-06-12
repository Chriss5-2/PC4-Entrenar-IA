FROM openjdk:11
WORKDIR /app
COPY src/*.java .
RUN javac *.java
CMD ["sh", "-c", "java Worker ${WORKER_ID} ${PORT} ${MONITOR_PORT}"]