# How to sniff TCP traffic data on RPC
Refer to https://superuser.com/questions/23180/whats-the-easiest-way-to-sniff-tcp-traffic-data-on-linux

For dev:
sudo tcpflow -i any -C -J port 18332

(also -J has been changed to -g in the latest release)

For prod:
sudo tcpflow -i any -C -J port 8332

(also -J has been changed to -g in the latest release)