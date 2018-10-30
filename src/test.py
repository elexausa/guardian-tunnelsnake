
import os
import socket    
import multiprocessing
import subprocess
import re
from getmac import get_mac_address

def pinger(job_q, results_q):
    """
    Runs ping as a subprocess to load ARP cache.

    :param job_q: Input job queue
    :param results_q: Resulting queue
    :return:
    """
    DEVNULL = open(os.devnull, 'w')
    while True:
        # Get IP from job
        ip = job_q.get()

        # Validation
        if ip is None:
            break

        # Attempt to ping IP
        try:
            subprocess.check_call(['ping', '-c1', ip], stdout=DEVNULL)
            results_q.put(ip)
        except:
            pass

def get_local_ip():
    """
    Grabs IP address of local machine.
    
    :return: Local IP address
    """
    # Create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Connect to local loopback
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()

    # Return IP address
    return ip

def map_network(pool_size=255):
    """
    Maps the network
    
    :param pool_size: Number of parallel ping processes
    :return: List of valid IP addresses
    """

    # Blank IP list to fill with findings
    ip_list = list()

    # Split IP
    ip_parts = get_local_ip().split('.')

    # Create base IP from local IP parts (192.168.X.YYY) 
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'

    # prepare the jobs queue
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    # Create pool
    pool = [multiprocessing.Process(target=pinger, args=(jobs, results)) for i in range(pool_size)]

    # Start all processes
    for p in pool:
        p.start()

    # Queue ping processes
    for i in range(1, 255):
        # Create job list with all possible IPs
        jobs.put(base_ip + '{0}'.format(i))

    # Stop jobs
    for p in pool:
        jobs.put(None)

    # Join all pools to ensure clean exit
    for p in pool:
        p.join()

    # Collect the results
    while not results.empty():
        ip = results.get()
        ip_list.append(ip)

    # Return
    return ip_list


if __name__ == '__main__':

    print('Mapping...')
    ip_list = map_network()

    for ip in ip_list:
        print ip

    arp_out = subprocess.check_output(['arp','-an'])
    addrs = re.findall(r"((\w{2,2}\:{0,1}){6})", arp_out)

    print addrs
