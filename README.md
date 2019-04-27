# CSC 573 - Internet Protocols Project 2

### Team:
* Rohil Shah (rshah8, 200204305)
* Sharvari Deshpande (shdeshpa, 200206230)

## Go-Back-N Automatic Repeat Request Protocol

To run the server: 
```
python3 go-back-n-server.py <server-port> <server-buffer-file> <probability>

eg. python3 go-back-n-server.py 7735 server-file.txt 0.05
```

To run the client: 
```
neelkapadia$ python3 go-back-n-client.py <server-host-name> <server-port-number> <client-sending-file> <window-size> <MSS>

eg. python3 go-back-n-client.py Rohils-MacBook-Pro.local 7735 client-file.txt 64 500
```
