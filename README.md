# IT347 Projects
### Project 1: Socket Programming
#### Server
Open a listener on TCP port 9020.   
Implement the server such that (all client commands are case sensitive):
* Client open receives a response of "Welcome to <your name>'s chat room<cr><lf>"
* Client request "help<cr><lf>" receives a response of a list of the commands and their syntax.
* Client request "test: words<cr><lf>" receives a response of "words<cr><lf>"
* Client request "name: <chatname><cr><lf>" receives a response of "OK<cr><lf>"
* Client request "get<cr><lf>" receives a response of the entire contents of the chat buffer.
* Client request "push: <stuff><cr><lf>" receives a response of "OK<cr><lf>" The result is that "<chatname>: <stuff>" is added as a new line to the chat buffer.
* Client request "getrange <startline> <endline><cr><lf>" receives a response of lines <startline> through <endline> from the chat buffer. getrange assumes a 0-based buffer. Your client should return lines <startline> <endline>
* Client request "SOME UNRECOGNIZED COMMAND<cr><lf>" receives a response "Error: unrecognized command: SOME UNRECOGNIZED COMMAND<cr><lf>"
* Client request "adios<cr><lf>" will quit the current connection. Checks for EOF or CLOSE SOCKET.

Socket timeout can be avoided by using the following python code:  
````
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
````

Similar functionality should be available from the operating system in other programming languages as well.
* All requests and responses must be terminated by a <cr><lf>
* The appearance of a a <cr><lf> signifies the end of a request or a response.
* Client commands can be issued in any order.
* If a name hasn't been set use "unknown"
* If you extend the protocol as part of your extra features, you must support the original protocol in a backwards compatible manner.
* Don't insert extra tabbing/formatting unless it is enabled via a protocol extension.

#### Client
1. Run the client by typing: ```$: <yourclientprogram> <ipaddress> <port>```  
2. Introduce yourself to the server:  ```$: <name>```  
3. Available commands:  
```
help  
test  
name  
get  
getrange  
adios  
```
All the commands and responses are written out to the screen for checking later.

#### Built With

* [Python3](http://www.dropwizard.io/1.0.2/docs/) - The web framework used