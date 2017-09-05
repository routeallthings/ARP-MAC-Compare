#!/usr/bin/env python
'''
---AUTHOR---
Name: Matt Cross
Email: routeallthings@gmail.com

---PREREQ---
INSTALL netmiko (pip install netmiko)
INSTALL textfsm (pip install textfsm)
INSTALL urllib (pip install urllib)

---VERSION---
VERSION 1.1

---THANKS---
networktocode - FSM templates

'''

'''Module Imports (Native)'''
import re
import getpass
import os
import unicodedata
import csv

'''Module Imports (Non-Native)'''
try:
	import netmiko
	from netmiko import ConnectHandler
except ImportError:
	netmikoinstallstatus = fullpath = raw_input ('Netmiko module is missing, would you like to automatically install? (Y/N): ')
	if "Y" in netmikoinstallstatus.upper() or "YES" in netmikoinstallstatus.upper():
		os.system('python -m pip install netmiko')
		import netmiko
		from netmiko import ConnectHandler
	else:
		print "You selected an option other than yes. Please be aware that this script requires the use of netmiko. Please install manually and retry"
		sys.exit()
try:
	import textfsm
except ImportError:
	textfsminstallstatus = fullpath = raw_input ('textfsm module is missing, would you like to automatically install? (Y/N): ')
	if "Y" in textfsminstallstatus.upper() or "YES" in textfsminstallstatus.upper():
		os.system('python -m pip install textfsm')
		import textfsm
	else:
		print "You selected an option other than yes. Please be aware that this script requires the use of textfsm. Please install manually and retry"
		sys.exit()
try:
	import urllib
except ImportError:
	urllibinstallstatus = fullpath = raw_input ('urllib module is missing, would you like to automatically install? (Y/N): ')
	if "Y" in urllibinstallstatus.upper() or "YES" in urllibinstallstatus.upper():
		os.system('python -m pip install urllib')
		import urllib
	else:
		print "You selected an option other than yes. Please be aware that this script requires the use of urllib. Please install manually and retry"
		sys.exit()
'''Global Variables'''
ipv4_address = re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')

'''Global Variable Questions'''
print ''
print 'L2 to L3 COMPARE SCRIPT'
print '#########################################################'
print 'The purpose of this is to make sure that all MAC entries '
print 'on a given switch have an IP associated on a L3 boundary.'
print '#########################################################'
print ''
print '----Questions for the L2 switch----'
sshl2ipq = raw_input ('Please enter the IP address of the L2 switch(s) (Separate by a comma): ')
if not ipv4_address.match(sshl2ipq):
		sshl2ipq = raw_input ('Please enter a correct IP address: ')
		if not ipv4_address.match(sshl2ipq):
			sys.exit('Incorrect IP address entered. Exiting script')
sshl2ipq = sshl2ipq.split(",")
sshl2userq = raw_input ('Enter the SSH username for the L2 switch: ')
sshl2password = getpass.getpass('Enter the SSH password for the L2 switch: ')
sshl2enable = getpass.getpass('Enter the SSH enable password for the L2 switch (optional): ')
sshl2type = raw_input ('Enter the OS of the L2 switch (IOS/XE/NXOS/Comware/Procurve): ')
if 'IOS' in sshl2type.upper() or 'XE' in sshl2type.upper() or 'NXOS' in sshl2type.upper():
	sshl2type = 'cisco_' + sshl2type.lower()
if 'COMWARE' in sshl2type.upper() or 'PROCURVE' in sshl2type.upper():
	sshl2type = 'hp_' + sshl2type.lower()
if not re.match("hp",sshl2type) and not re.match("cisco",sshl2type):
	print 'Incorrect input, please enter one of the compatible switch OS'
	sys.exit()
sshl2l3q = raw_input ('Is the L3 boundary on the same switch? (Y/N): ')
if "N" in sshl2l3q.upper():
	print '----Questions for the L3 switch----'
	sshl3ipq = raw_input ('Please enter the IP address of the L3 switch(s) (Separate by a comma): ')
	if not ipv4_address.match(sshl3ipq):
		sshl3ipq = raw_input ('Please enter a correct IP address: ')
		if not ipv4_address.match(sshl3ipq):
			sys.exit('Incorrect IP address entered. Exiting script')
	sshl3ipq = sshl3ipq.split(",")
	sshl3userq = raw_input ('Enter the SSH username for the L3 switch: ')
	sshl3password = getpass.getpass('Enter the SSH password for the L3 switch: ')
	sshl3enable = getpass.getpass('Enter the SSH enable password for the L3 switch (optional): ')
	sshl3type = raw_input ('Enter the OS of the L3 switch (IOS/XE/NXOS/Comware/Procurve): ')
	if 'IOS' in sshl3type.upper() or 'XE' in sshl3type.upper() or 'NXOS' in sshl3type.upper():
		sshl3type = 'cisco_' + sshl3type.lower()
	if 'COMWARE' in sshl3type.upper() or 'PROCURVE' in sshl3type.upper():
		sshl3type = 'hp_' + sshl3type.lower()
	if not re.match("hp",sshl3type) and not re.match("cisco",sshl3type):
		print 'Incorrect input, please enter one of the compatible switch OS'
		sys.exit()
else:
	print 'L2 and L3 are on the same switch'
	sshl3ipq = sshl2ipq
	sshl3userq = sshl2userq
	sshl3password = sshl2password
	sshl3enable = sshl2enable
	sshl3type = sshl2type
saveresults = raw_input ('Do you want to save the results to a file? (Y/N): ')
if "Y" in saveresults.upper() or "YES" in saveresults.upper():
	savepath = raw_input ('Please enter the path of the file? (e.g. C:\Python27\Results.csv): ')
	if savepath == '':
		savepath = 'C:\Python27\Results.csv'
'''FSM section L2'''
if "hp_comware" in sshl2type:
	fsmmactemplateurl = "https://raw.githubusercontent.com/networktocode/ntc-templates/master/templates/hp_comware_display_mac-address.template"
if "hp_procurve" in sshl2type:
	fsmmactemplateurl = "https://raw.githubusercontent.com/routeallthings/ARP-MAC-Compare/master/hp_procurve_show_mac_address.template"
if "cisco_ios" in sshl2type or "cisco_xe" in sshl2type:
	fsmmactemplateurl = "https://raw.githubusercontent.com/networktocode/ntc-templates/master/templates/cisco_ios_show_mac-address-table.template"
if "cisco_nxos" in sshl2type:
	fsmmactemplateurl = "https://raw.githubusercontent.com/networktocode/ntc-templates/master/templates/cisco_nxos_show_mac_address-table.template"
urllib.urlretrieve(fsmmactemplateurl,'fsmmactemplate.fsm')
fsmmactemplatefile = open("fsmmactemplate.fsm")
fsmmactemplate = textfsm.TextFSM(fsmmactemplatefile)
'''FSM section L3'''
if "hp_comware" in sshl3type:
	fsmarptemplate = "https://raw.githubusercontent.com/networktocode/ntc-templates/master/templates/hp_comware_display_arp.template"
if "hp_procurve" in sshl3type:
	fsmarptemplate = "https://raw.githubusercontent.com/routeallthings/ARP-MAC-Compare/master/hp_procurve_show_arp.template"
if "cisco_ios" in sshl3type or "cisco_xe" in sshl2type:
	fsmarptemplate = "https://raw.githubusercontent.com/networktocode/ntc-templates/master/templates/cisco_ios_show_ip_arp.template"
if "cisco_nxos" in sshl3type:
	fsmarptemplate = "https://raw.githubusercontent.com/networktocode/ntc-templates/master/templates/cisco_nxos_show_ip_arp_detail.template"
urllib.urlretrieve(fsmarptemplate,'fsmarptemplate.fsm')
fsmarptemplatefile = open("fsmarptemplate.fsm")
fsmarptemplate = textfsm.TextFSM(fsmarptemplatefile)
'''Starting Script'''
'''L2'''
print '---------------------------------------------------------'
print 'Connecting to the L2 switch'
for sshl2ip in sshl2ipq:
	l2net_connect = ConnectHandler(device_type=sshl2type, ip=sshl2ip, username=sshl2userq, password=sshl2password)
	l2devicehostname = l2net_connect.find_prompt()
	if '>' in l2devicehostname:
		l2net_connect.send_command("enable")
		l2net_connect.send_command(sshl2enable)
		l2devicehostname = l2net_connect.find_prompt()
	l2devicehostname = l2devicehostname.strip('#')
	print 'Successfully connected to ' + l2devicehostname
	print 'Getting MAC address table'
	if 'cisco' in sshl2type:
		l2mactable = l2net_connect.send_command("show mac address-table dynamic")
		if 'Invalid input' in l2mactable:
			l2net_connect.send_command("show mac-address-table")
	if 'hp' in sshl2type:
		l2mactable = l2net_connect.send_command("show mac-address")
	l2mactable = fsmmactemplate.ParseText(l2mactable)
	try:
		l2mactablefull.extend(l2mactable)
	except NameError:
		l2mactablefull = []
		l2mactablefull.extend(l2mactable)
	l2net_connect.disconnect()
print '---------------------------------------------------------'
'''L3'''
print 'Connecting to the L3 switch'
for sshl3ip in sshl3ipq:
	l3net_connect = ConnectHandler(device_type=sshl3type, ip=sshl3ip, username=sshl3userq, password=sshl3password)
	l3devicehostname = l3net_connect.find_prompt()
	if '>' in l3devicehostname:
		l3net_connect.send_command("enable")
		l3net_connect.send_command(sshl3enable)
		l3devicehostname = l3net_connect.find_prompt()
	l3devicehostname = l3devicehostname.strip('#')
	print 'Successfully connected to ' + l3devicehostname
	print 'Getting ARP table for comparison'
	if 'cisco' in sshl3type:
		l3arptable = l3net_connect.send_command("show ip arp")
		if 'Invalid input' in l3arptable:
			l3net_connect.send_command("show arp")
	if 'hp' in sshl3type:
		l3arptable = l3net_connect.send_command("show arp")
	l3arptable = fsmarptemplate.ParseText(l3arptable)
	try:
		l3arptablefull.extend(l3arptable)
	except NameError:
		l3arptablefull = []
		l3arptablefull.extend(l3arptable)
	l3net_connect.disconnect()
print '---------------------------------------------------------'
print 'Comparing MAC address table to ARP table'
if "Y" in saveresults.upper() or "YES" in saveresults.upper():
	with open(savepath, 'wb') as csvfile:
		fieldnames = ['mac_add', 'mac_vlan', 'mac_int', 'arp_ip', 'arp_int']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for mac in l2mactablefull:
			if 'cisco' in sshl2type:
				macaddress = mac[0]
				macvlan = mac[2]
				macinterface = mac[3]
			if 'hp' in sshl2type:
				macaddress = mac[0]
				macvlan = mac[2]
				macinterface = mac[1]
			macaddress = macaddress.encode('ascii','ignore')
			macaddress = macaddress.replace ('-','')
			macaddress = macaddress.replace ('.','')
			for ipadd in l3arptablefull:
				if 'cisco' in sshl3type:
					arpmac = ipadd[2]
					arpip = ipadd[0]
					arpint = ipadd[4]
				if 'hp' in sshl3type:
					arpmac = ipadd[1]
					arpip = ipadd[0]
					arpint = ipadd[3]
				arpmac = arpmac.encode('ascii','ignore')
				arpmac = arpmac.replace ('-','')
				arpmac = arpmac.replace ('.','')
				if macaddress == arpmac:
					foundmatch = 'true'
					break
				else:
					foundmatch = 'false'
			if 'true' in foundmatch:
				print 'Found match on L2 interface ' + macinterface + '. The IP address found was ' + arpip + ' in ' + arpint + '.'
				writer.writerow({'mac_add': macaddress, 'mac_vlan': macvlan, 'mac_int': macinterface, 'arp_ip': arpip, 'arp_int': arpint})
			else:
				print 'No IP address found for MAC ' + macaddress + ' on interface ' + macinterface + ' in vlan' + macvlan + '.'
				writer.writerow({'mac_add': macaddress, 'mac_vlan': macvlan, 'mac_int': macinterface})
			foundmatch = 'false'
else:
	for mac in l2mactablefull:
		if 'cisco' in sshl2type:
			macaddress = mac[0]
			macvlan = mac[2]
			macinterface = mac[3]
		if 'hp' in sshl2type:
			macaddress = mac[0]
			macvlan = mac[2]
			macinterface = mac[1]
		macaddress = macaddress.encode('ascii','ignore')
		macaddress = macaddress.replace ('-','')
		macaddress = macaddress.replace ('.','')
		for ipadd in l3arptablefull:
			if 'cisco' in sshl3type:
				arpmac = ipadd[2]
				arpip = ipadd[0]
				arpint = ipadd[4]
			if 'hp' in sshl3type:
				arpmac = ipadd[1]
				arpip = ipadd[0]
				arpint = ipadd[3]
			arpmac = arpmac.encode('ascii','ignore')
			arpmac = arpmac.replace ('-','')
			arpmac = arpmac.replace ('.','')
			if macaddress == arpmac:
				foundmatch = 'true'
				break
			else:
				foundmatch = 'false'
		if 'true' in foundmatch:
			print 'Found match on L2 interface ' + macinterface + '. The IP address found was ' + arpip + ' in ' + arpint + '.'
		else:
			print 'No IP address found for MAC ' + macaddress + ' on interface ' + macinterface + ' in vlan' + macvlan + '.'
		foundmatch = 'false'
print '---------------------------------------------------------'
print 'Cleaning up'
try:
	os.remove('fsmmactemplate.fsm')
except:
	print 'Please manually remove the temporary file fsmmactemplate.fsm'
try:
	os.remove('fsmarptemplate.fsm')
except:
	print 'Please manually remove the temporary file fsmarptemplate.fsm'
l2mactablefull = []
l3arptablefull = []
print '---------------------------------------------------------'
print 'Script Complete'