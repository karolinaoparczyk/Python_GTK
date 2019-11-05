#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libclient

sel = selectors.DefaultSelector()


def create_request(action, value):
    if action == "search" or action == 'delete':
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, encoding="utf-8"),
        )


def start_connection(host, port, request):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

def define_connection(action, value):
	host, port = '127.0.0.1', 65432
	request = create_request(action, value)
	print(request)
	start_connection(host, port, request)
	try:
		while True:
			events = sel.select(timeout=1)
			for key, mask in events:
				message = key.data
			try:
				answer = message.process_events(mask)
			except Exception:
				print(
				"main: error: exception for",
				f"{message.addr}:\n{traceback.format_exc()}",
				)
				message.close()
			# Check for a socket being monitored to continue.
			if not sel.get_map():
				break
	except KeyboardInterrupt:
		print("caught keyboard interrupt, exiting")
	#finally:
	#	sel.close()
	return answer

def close():
	sel.close()
