# CSC 573 - Internet Protocols Project 2

## Go-Back-N Automatic Repeat Request Protocol

Step 1: Install all required packages (most are default in Python 3.x)

Step 2: Run the server
```
python3 go-back-n-server.py <server-port> <server-buffer-file> <probability>

eg. python3 go-back-n-server.py 20930 server-file.txt 0.05
```

Step 3: Run the client
```
neelkapadia$ python3 go-back-n-client.py <server-host-name> <server-port-number> <client-sending-file> <window-size> <MSS>

eg. python3 go-back-n-client.py MacBook-Pro.local 20930 client-file.txt 1 500
```

Step 4: Observe the output of the client to get information on the time required to send, server info etc.

## Selective Repeat Automatic Repeat Request Protocol

Step 1: Install all required packages (most are default in Python 3.x)

Step 2: Run the server
```
python3 selective-repeat-server.py <server-port> <server-buffer-file> <probability>

eg. python3 selective-repeat-server.py 20930 server-file.txt 0.05
```

Step 3: Run the client
```
python3 selective-repeat-client.py <server-host-name> <server-port-number> <client-sending-file> <window-size> <MSS>

eg. python3 selective-repeat-client.py MacBook-Pro.local 20930 client-file.txt 1 500
```

Step 4: Observe the output of the client to get information on the time required to send, server info etc.