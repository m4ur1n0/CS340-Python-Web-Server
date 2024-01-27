import socket
import sys

# exit code key
# 0 = success 
# 1 = issue with http prefix
# 3 = too many redirects 
# 4 = response code >= 400
# 5 = content type not html

# IMPORTANT GLOBAL VARIABLES -----
REDIRECT_COUNT = 0

# --------------------------------


def make_get_request(host, file_path, port):
    # expects strings host (hostname) and file_path
    # returns the decoded string version of the response

    # create a socket prepared for Address From Internet
    # then connect it to the url provided
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostbyname(host), port))

    get_request = "GET /"+ file_path + " HTTP/1.0\r\n" + "Host: " + host + "\r\n\r\n"
    s.send(get_request.encode("utf-8"))

    # now listen on the port until we receive everything we need, save to response
    response = b""
    while True:
        
        block = s.recv(4096)
        if not block:
            break

        response += block

    s.close()
    return response.decode("utf-8")




def get_resp_code(http_resp):
    # THIS FUNCTION EXPECTS AN ALREADY DECODED STRING

    # may convert to using regexps later, rn should be enough that every response will start
    # with HTTP/1.1 etc. etc.

    # assuming 'HTTP/1.X ' is the beginning, that's always 9 chars
    code_sect = http_resp.split("\n")[0][9:-1] # < this will include the plaintxt version

    pair = [int(code_sect[0:3]), code_sect[4:]]



    return pair

def pull_body_from_resp(resp):
    # expects a fully dedoded string http response
    # the rest of the program expects this to return a string: the body
    lines = resp.split("\n")
    body_start = 0

  
    for i, line in enumerate(lines):
        if line == "\r":

            body_start = i + 1
            break
    
    body = "\n".join(lines[body_start:])
    return body

def get_content_type(resp):
    lines = resp.split("\n")
    for line in lines:
        if (line.lower()[0:12] == "content-type"):
            return line[14:23]
    
    return 0

def get_redirect_url(body):
    # expects THE BODY of a fully decoded string http response
    # the rest of the program expects this to return a string: the url to be redirected to
    new = ""
    for i, char in enumerate(body):
        if (body[i:(i + 9)].upper() == "<A HREF=\""):
            # in this situation, i + 9 is the index of the 'h'
            # in 'http://newurl.example' 
            for j in range((i+ 9), len(body)):
                if (body[j] == '"'):
                    break
                else:
                    new = new + body[j]
            
            break

    return new


def deal_w_resp_msg(resp):
    global REDIRECT_COUNT
    # expects a fully decoded string http response

    resp_code_pair = get_resp_code(resp)
    code = resp_code_pair[0]

    # error codes (400+) get body printed but exited as unsuccessful
    if (code >= 400):
        print(pull_body_from_resp(resp))
        sys.exit(4)
    
    # redirects
    if (code == 301 or code == 302):
        # debug ------
        #print("\nBODY:\n" + pull_body_from_resp(resp) + "\n")
        # debug ------
        new_url = get_redirect_url(pull_body_from_resp(resp))
        REDIRECT_COUNT += 1
        if (REDIRECT_COUNT >= 11):
            sys.exit(3)
        else:
            print("Redirected to: " + new_url, file=sys.stderr)
            # debug --------
            #print("ATTEMPT: ", REDIRECT_COUNT, "\n")
            # debug --------
            curl(new_url)

    if (code == 200):
        REDIRECT_COUNT = 0
        if (get_content_type(resp).lower() != "text/html"):
            exit(5)
        else:
            print(pull_body_from_resp(resp))
            sys.exit(0)




def deal_w_url(url):
    # expects a string url, straight from
    # returns a tuple with the hostname and the file path as seperate strings
    
    # if it tries to visit a secure server shut 'er down, but special
    if (url[0:8] == "https://"):
        print("Part of my bad boy lifestyle means I'm unwilling to visit a secure page.", file=sys.stderr)
        sys.exit(1)

    if (url[0:7] != "http://"):
        sys.exit(1)

    
    # http://portquiz.net:8080/
    # the lookup doesn't work with the http:// prefix, as it tries to get host by name
    # including the prefix as a part of the hostname, so if the prefix exists it must be removed
    # we also need to find the file path
    url = url.replace("http://", "")
    parts = url.split("/")
    host = parts[0]
    index = -1
    try:
        index = host.index(':')
    except:
        pass
    

    port = ""
    if (index >= 0):
        for i, char in enumerate(host):
            if (i < index):
                continue

            try:

                num = int(char)
                port += char
            except:
                continue
        
        intPort = int(port)
        return (host[0:index], "/".join(parts[1:]), intPort)

    else:
        file_path = "/".join(parts[1:])
        #print(file_path)
        return (host, file_path, 80)
    
    

def curl(url):
    # uses all the helper functions and shit

    hostNpath = deal_w_url(url)
    # waste of space complexity here, oh well, it's a small program
    host = hostNpath[0]
    path = hostNpath[1]
    port = hostNpath[2]
    
    response = make_get_request(host, path, port)
    #print(response)

    # the rest is done by deal_w_resp_message
    deal_w_resp_msg(response)

    
    # body = pull_body_from_resp(response)
    # print("\n\nBODY\n\n" + body)

    

    




# ----- 'MAIN METHOD' STARTS HERE -------
# STILL NEED TO LET IT ALLOW PORT #

url = sys.argv[1]
curl(url)



