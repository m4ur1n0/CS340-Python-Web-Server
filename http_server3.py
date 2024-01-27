from decimal import Decimal
import math
import socket
import sys
import os
import json


# failure exit code key
# 1 = port number lower than 1024 or not an int

# def get_rid_of_trailing_0s(num_list):
#     new_num_list = []
#     for num in num_list:
#         if num.is_integer():
#             new_num_list.append(math.floor(num))
#         else:
#             new_num_list.append(num)

#     return new_num_list

# def parse_query(q_str):

def get_rid_of_trailing_0s(num_list):
    new_num_list = []
    for num in num_list:
        if isinstance(num, Decimal):
            num_str = str(num.quantize(Decimal('1.'), rounding='ROUND_DOWN'))
        elif num.is_integer():
            num_str = str(int(num))
        else:
            num_str = str(num)

        new_num_list.append(num_str)

    return new_num_list

def parse_query(q_str):
    # expects only the variable parts of a url query
    # i.e. if the URL query starts: product?a=12&b=60....
    # then the q_str parameter is expected to start:
    # a=12&b=60..... etc.
    # it will return a list of floats corresponding to the vars
    # if the vars are improperly formatted or there are none,
    # it will return an int, i.e. the proper return code

    # 400 Bad Request for 'GET /product?a="blah"'

    assignments = q_str.split("&")
    vals = []
    r400 = False
    for var in assignments:
        parts = var.split("=")
        try:
            vals.append(float(parts[1]))
        except:
            r400 = True
            break

    
    if r400:
        return 400
    else:
        return vals


def receive(client_sock):
    recvd = b""
    while (True):
        # not worrying about if .htm is in the string until I know the above condition is even relevant
        chunk = client_sock.recv(1024)
        if (not chunk):
            break

        recvd += chunk

        if (b"\n\r\n\r" in recvd) or (b"\n\n" in recvd) or (b"\r\r" in recvd) or (b"\r\n"  in recvd):
            break


    # now recvd should be a full http request made to our server
    response = recvd.decode("utf-8")
    # debug --------
    # print("\n\n" + response + "\n\n")
    # debug -------- 
    return response

def get_result(query):
    # expects a file path relevant to this directory (not beginning with '/')
    # returns a tuple with the header and the path to serve
    # now we have to make sure the file exists, and that its an html file
    return_body = ""
    code = ""
    code_dict = {"200": "OK", "400": "Bad Request", "404": "Not Found"}


    if (query[0:7].lower() != "product"):
        content_type = "Content-Type: text/html"
        code = "404"
        status_line = "HTTP/1.0 " + code + " " + code_dict.get(code)
        content_length = "Content-Length: " + str(os.path.getsize("404.html"))
        return_path = "404.html"
        header = status_line + "\n" + content_type + "\n" + content_length + "\n\n"
        return [header, return_path]



    # the only JSON we're prepared to process is a GET like:
    # GET /product?a=1&b=2&c=3 etc etc
    query_parts = query.split("?")


    nums = parse_query(query_parts[1])
    if (nums == 400):
        code = "400"
    else:
        code = "200"
    
    
    status_line = "HTTP/1.0 " + code + " " + code_dict.get(code)


    

    # assign content lengths based on respective file sizes

    if (code == "400"):
        content_type = "Content-Type: text/html"
        content_length = "Content-Length: " + str(os.path.getsize("400.html"))
        return_path = "400.html"
        header = status_line + "\n" + content_type + "\n" + content_length + "\n\n"
        return [header, return_path]
    
    if (code == "200"):
        content_type = "Content-Type: application/json"
        total = 1.0
        for num in nums:
            total *= num
            
        for i in range(len(nums)):
            if nums[i] == float('inf'):
                nums[i] = 'inf'
            if nums[i] * -1 == float('inf'):
                nums[i] = '-inf'
        

        if total == float('inf'):
            total = 'inf'
        elif -total == float('inf'):
            total = '-inf'

        # get rid of trailing 0's for proper formatting
        #nums = get_rid_of_trailing_0s(nums)
        if (isinstance(total, float) and total.is_integer()):
            total = math.floor(total)

        body = {
            "operation": "product",
            "operands": nums,
            "result": total
        }

        json_resp = json.dumps(body, indent=2)
        content_length = "Content-Length: " + str(len(json_resp.encode("utf-8")))
        # instead, here we must put the effects of the request
        ok_resp = status_line + "\n" + content_type + "\n" + content_length + "\n\n" + json_resp

        return [ok_resp]



    


# set port to the argument passed on the command line
port = sys.argv[1]
try:
    port = int(port)
except:
    print("port numbers are supposed to be numbers...", file=sys.stderr)
    exit(1)

if (port < 1024):
    print("Port # reserved", file=sys.stderr)
    exit(1)

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host the server on port port, "" means it doesn't care what ip tries to connect to it
server_sock.bind(("", port))
# allowing for a connection backlog of 4 to minimize rejections, but not waste resources,
# as this is a small app. it will be very rare for it to service multiple connections at once 
server_sock.listen(4)


while True:
    # socket.accept() will pause the process until a socket is connected
    client_sock, client_addy = server_sock.accept()
    # debug ---------
    # print("Accepted connection from:", client_addy)
    # debug --------- 

    response = receive(client_sock)

    # if we don't get a GET request, close the connection and move on
    if (response[0:4].lower() != "get "):
        
        # Only configured to handle get requests :( 
        client_sock.close()
        continue

    # assuming it WAS a get request, now we know how to find the file path
    # the file path is everything after the '/' between the first two
    # spaces in the first line of the get request 
    lines = response.split("\n")
    request = lines[0].split(" ")[1][1:]
    # debug --------
    # print(file_path)
    # debug --------

    # debug ------
    # print(file_path)
    # debug ------

    # this all has to change depending on how I build the response body (i.e. why do I need to use JSON lib)

    res = get_result(request)

    if (len(res) == 2):
        header = res[0]
        path = res[1]
        # now to push the header and the file back through the socket
        # print(header)
        client_sock.send(header.encode("utf-8"))
        with open(path, "r") as file:
            data = file.read(1024)  # Read the file in chunks
            while data:
                client_sock.send(data.encode("utf-8"))
                data = file.read(1024)
    else:
        client_sock.send(res[0].encode("utf-8"))

    # now we've transmitted the file and can close the socket
    client_sock.close()

    