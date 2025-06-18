config = """version 15.2
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname TestSwitch
!
boot-start-marker
boot-end-marker
!
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
!
no aaa new-model
system mtu routing 1500
!
interface GigabitEthernet0/1
 description Link to Server
 switchport access vlan 10
 switchport mode access
 spanning-tree portfast
!
interface GigabitEthernet0/2
 description Trunk to Core
 switchport trunk encapsulation dot1q
 switchport mode trunk
!
interface GigabitEthernet0/3
 description DHCP Test Interface
 ip address dhcp
 no shutdown
!
interface Vlan1
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface Vlan10
 description Server VLAN
 ip address 10.0.10.1 255.255.255.0
 no shutdown
!
interface Vlan20
 description VRF VLAN
 vrf forwarding Blue
 ip address 10.10.10.1 255.255.255.0
 no shutdown
!
ip default-gateway 192.168.1.254
!
access-list 10 permit 192.168.1.0 0.0.0.255
access-list 10 deny any
!
ip access-list extended WEB_ACL
 permit tcp any any eq 80
 permit tcp any any eq 443
 deny ip any any
!
radius-server host 192.168.1.100 auth-port 1812 acct-port 1813 key secret123
radius-server host 192.168.1.101 key radius_key
!
tacacs-server host 192.168.1.200 port 49 key tacacs_secret
tacacs-server host 192.168.1.201
!
logging host 192.168.1.50
logging 192.168.1.51
!
line con 0
line vty 0 4
 login
line vty 5 15
 login
!
end"""
