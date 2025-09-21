import socket
import sys
from queue import Queue
import threading
from datetime import datetime
import os

# Очистка экрана
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

clear()




if len(sys.argv) < 3:
    print("Использование: python3 main.py <file_with_ips> <ports_comma_separated> [threads]")
    sys.exit(1)

ip_file = sys.argv[1]
ports_input = sys.argv[2]
threads_count = int(sys.argv[3]) if len(sys.argv) > 3 else 200  # по умолчанию 200 потоков


try:
    with open(ip_file, 'r') as f:
        hosts = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"Ошибка при чтении файла: {e}")
    sys.exit(1)


try:
    ports = [int(p.strip()) for p in ports_input.split(',') if p.strip().isdigit()]
except Exception as e:
    print(f"Ошибка при разборе портов: {e}")
    sys.exit(1)

print("-"*50)
print(f"Targets: {hosts}")
print(f"Ports: {ports}")
print(f"Threads: {threads_count}")
print("Scanning started at:", datetime.now())
print("-"*50)

queue = Queue()
total_tasks = len(hosts) * len(ports)
completed_tasks = 0
lock = threading.Lock()  


for host in hosts:
    for port in ports:
        queue.put((host, port))

open_ports = []

def scan(host, port):
    s = socket.socket()
    s.settimeout(3)
    try:
        result = s.connect_ex((host, port))
        if result == 0:
            with lock:
                print(f"[OPEN] {host}:{port}")
                open_ports.append((host, port))
                
                with open("results.txt", "a") as f:
                    f.write(f"{host}\n")
    except Exception:
        pass
    finally:
        s.close()

def worker():
    global completed_tasks
    while not queue.empty():
        host, port = queue.get()
        scan(host, port)
        with lock:
            completed_tasks += 1
            percent = (completed_tasks / total_tasks) * 100
            print(f"\rProgress: {percent:.2f}% ({completed_tasks}/{total_tasks})", end='', flush=True)


threads_count = min(threads_count, queue.qsize())
threads = []

for _ in range(threads_count):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("\n" + "-"*50)
print(f"Scanning completed at: {datetime.now()}")
print(f"Open ports found: {open_ports}")
print("Результаты сохранены в results.txt")
