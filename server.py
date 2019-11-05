#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libserver

sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False) #otherwise all other sockets are left waiting for this one (hang state)
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)


host, port = '127.0.0.1', 65432
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        # key.fileobj - socket object
        # mask - event mask of ready operations
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                #else it's a client socket that's already been accepted
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print("main: error: exception for %s\n%s" % (message.addr, traceback.format_exc()))
                    message.close()
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
