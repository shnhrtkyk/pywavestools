import requests
import re
from ipwhois import IPWhois
import argparse

parser = argparse.ArgumentParser(description='List nodes of the Waves network')
parser.add_argument('-a', '--all', action='store_true', help='includes removed or temporary offline nodes')

args = parser.parse_args()

checked_nodes=[]

def getPeers(node):
    peers = []
    try:
        tmp_peers = ''
        if node not in checked_nodes:
            checked_nodes.append(node)
            try:
                tmp_peers = requests.get(node + '/peers/connected', timeout=0.5).json()['peers']
                print("Getting peers from %s" % node)
            except:
                pass
            if args.all:
                try:
                    tmp_peers = tmp_peers + requests.get(node + '/peers/all', timeout=0.5).json()
                except:
                    pass
            if len(tmp_peers)>0:
                peers = peers + tmp_peers
                for p in tmp_peers:
                    match = re.search('.*\/(.*):.*', p['address'])
                    if match:
                        ip = match.group(1)
                        tmp_peers = getPeers('http://' + ip + ':6869')
                        peers = peers + tmp_peers
    except:
        pass
    return peers

peers = getPeers('https://nodes.wavesnodes.com') + getPeers('http://127.0.0.1:6869')
nodes_by_country = {}

print("Getting IP networks info...")

nodes=[('','','','','')]
for peer in peers:
    match = re.search('.*\/(.*):.*', peer['address'])
    if match:
        ip = match.group(1)
        if ip not in zip(*nodes)[1]:
            try:
                res = IPWhois(ip).lookup_whois()['nets'][0]
                country = ''
                net = ''
                descr = ''
                try:
                    if res['country']:
                        country = res['country']
                    if res['name']:
                        net = res['name']
                    if res['description']:
                        descr = res['description'].replace('\n', ' ')
                except:
                    pass
                try:
                    name = peer['peerName'][:30]
                    if name[0]=='<':
                        name = ''
                except:
                    name = ''
                nodes.append((name, ip, country[:2], net[:20], descr[:40]))
                if country in nodes_by_country.keys():
                    nodes_by_country[country] += 1
                else:
                    nodes_by_country[country] = 1
            except:
                pass
                
nodes = nodes[1:]
print
print
print("-" * 120)
print("  #  Node name                      IP address    Country  Network              Network description")
print("-" * 120)

for i, node in enumerate(sorted(nodes, key=lambda x: x[2])):
    print ("%3d  %-30s %-15s  %-2s    %-20s %-40s" % (i + 1, node[0], node[1], node[2], node[3], node[4]))
    
print("-" * 120)
print
print("Country  # of nodes")
print("-" * 20)
for c in sorted(nodes_by_country.items(), key=lambda x: -x[1]):
    print ("  %-2s        %3d" % (c[0], c[1]))
print("-" * 20)
print ("            %3d" % sum(nodes_by_country.values()))
print
print("-" * 120)
