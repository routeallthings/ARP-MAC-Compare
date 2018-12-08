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
	netmikoinstallstatus = raw_input ('Netmiko module is missing, would you like to automatically install? (Y/N): ')
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
	textfsminstallstatus = raw_input ('textfsm module is missing, would you like to automatically install? (Y/N): ')
	if "Y" in textfsminstallstatus.upper() or "YES" in textfsminstallstatus.upper():
		os.system('python -m pip install textfsm')
		import textfsm
	else:
		print "You selected an option other than yes. Please be aware that this script requires the use of textfsm. Please install manually and retry"
		sys.exit()
try:
	import urllib
except ImportError:
	urllibinstallstatus = raw_input ('urllib module is missing, would you like to automatically install? (Y/N): ')
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
l2uplinkq = raw_input ('Do you want to ignore interfaces with more than 3 MAC addresses? (Y/N): ')
l2ignorevlanq = raw_input ('Do you want to exempt specific VLANs from the lookup? (Y/N): ')
if "Y" in l2ignorevlanq.upper():
	l2ignorevlan = raw_input ('Exempted VLAN #s from the MAC lookup (separate by comma): ')
	l2ignorevlan = l2ignorevlan.split(",")
if "cisco_xe" in sshl2type:
	l2healthcheckq = raw_input ('Do you want to look for interface errors (Duplexing Issues)? (Y/N): ')
else:
	l2healthcheckq = 'N'
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
if "cisco_ios" in sshl2type:
	fsmmactemplateurl = "https://raw.githubusercontent.com/networktocode/ntc-templates/master/templates/cisco_ios_show_mac-address-table.template"
if "cisco_xe" in sshl2type:
	fsmmactemplateurl = "https://raw.githubusercontent.com/routeallthings/ARP-MAC-Compare/master/cisco_xe_show_mac_address.template"
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
if "cisco_ios" in sshl3type or "cisco_xe" in sshl3type:
	fsmarptemplate = "https://raw.githubusercontent.com/networktocode/ntc-templates/master/templates/cisco_ios_show_ip_arp.template"
if "cisco_nxos" in sshl3type:
	fsmarptemplate = "https://raw.githubusercontent.com/routeallthings/ARP-MAC-Compare/master/cisco_nxos_show_ip_arp.template"
urllib.urlretrieve(fsmarptemplate,'fsmarptemplate.fsm')
fsmarptemplatefile = open("fsmarptemplate.fsm")
fsmarptemplate = textfsm.TextFSM(fsmarptemplatefile)
'''FSM section HealthCheck'''
if "cisco_xe" in sshl2type and "Y" in l2healthcheckq.upper():
	fsmhealthtemplateurl = "https://raw.githubusercontent.com/routeallthings/ARP-MAC-Compare/master/cisco_xe_show_interface_errors%20.template"
	urllib.urlretrieve(fsmhealthtemplateurl,'fsmhealthtemplate.fsm')
	fsmhealthtemplatefile = open("fsmhealthtemplate.fsm")
	fsmhealthtemplate = textfsm.TextFSM(fsmhealthtemplatefile)
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
		l2mactable = l2net_connect.send_command("show mac address-table | exclude CPU")
		if 'Invalid input' in l2mactable:
			l2mactable = l2net_connect.send_command("show mac-address-table")
		l2mactable = fsmmactemplate.ParseText(l2mactable)
		if 'Y' in l2uplinkq.upper():
			for mac in l2mactable:
				if 'cisco_ios' in sshl2type:
					macinterface = mac[3]
				if 'cisco_xe' in sshl2type:
					macinterface = mac[3]
				if 'cisco_nxos' in sshl2type:
					macinterface = mac[6]
				try:
					l2macinttablefull.append(macinterface)
				except NameError:
					l2macinttablefull = []
					l2macinttablefull.append(macinterface)
			for mac in l2mactable:
				macinterface = mac[3]
				macinterfacename = macinterface.encode('ascii','ignore')
				l2macintcount = l2macinttablefull.count(macinterface)
				if l2macintcount < 3:
					try:
						l2mactablenew.append(mac)
					except NameError:
						l2mactablenew = []
						l2mactablenew.append(mac)
				else:
					l2macintcountstr = str(l2macintcount)
					'''print 'Interface ' + macinterfacename + ' has over ' + l2macintcountstr + ' mac addresses associated. Assuming uplink to another switch.'''
			l2mactable = l2mactablenew
		if 'Y' in l2ignorevlanq.upper():	
			l2mactablenew = []
			for mac in l2mactable:
				if 'cisco_ios' in sshl2type:
					macvlan = mac[2]
				if 'cisco_xe' in sshl2type:
					macvlan = mac[2]
				if 'cisco_nxos' in sshl2type:
					macvlan = mac[0]
				if not l2ignorevlan.count(macvlan) == 1:
					l2mactablenew.append(mac)
			l2mactable = l2mactablenew
	if 'hp' in sshl2type:
		l2mactable = l2net_connect.send_command("show mac-address")
		l2mactable = fsmmactemplate.ParseText(l2mactable)
		if 'Y' in l2uplinkq.upper():
			for mac in l2mactable:
				macinterface = mac[1]
				try:
					l2macinttablefull.append(macinterface)
				except NameError:
					l2macinttablefull = []
					l2macinttablefull.append(macinterface)
			for mac in l2mactable:
				macinterface = mac[1]
				macinterfacename = macinterface.encode('ascii','ignore')
				l2macintcount = l2macinttablefull.count(macinterface)
				if l2macintcount < 3:
					try:
						l2mactablenew.append(mac)
					except NameError:
						l2mactablenew = []
						l2mactablenew.append(mac)
				else:
					l2macintcountstr = str(l2macintcount)
					'''print 'Interface ' + macinterfacename + ' has over ' + l2macintcountstr + ' mac addresses associated. Assuming uplink to another switch.'''
			l2mactable = l2mactablenew
		if 'Y' in l2ignorevlanq.upper():	
			l2mactablenew = []
			for mac in l2mactable:
				macvlan = mac[2]
				if not l2ignorevlan.count(macvlan) == 1:
					l2mactablenew.append(mac)
			l2mactable = l2mactablenew	
	try:
		l2mactablefull.extend(l2mactable)
	except NameError:
		l2mactablefull = []
		l2mactablefull.extend(l2mactable)
	if "Y" in l2healthcheckq.upper():
		l2healthtable = l2net_connect.send_command("show interface counters errors")
		l2healthtable = fsmhealthtemplate.ParseText(l2healthtable)
		try:
			l2healthtablefull.extend(l2healthtable)
		except NameError:
			l2healthtablefull = []
			l2healthtablefull.extend(l2healthtable)
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
			l3arptable = l3net_connect.send_command("show arp")
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
			if 'cisco_ios' in sshl2type:
				macaddress = mac[0]
				macvlan = mac[2]
				macinterface = mac[3]
			if 'cisco_xe' in sshl2type:
				macaddress = mac[0]
				macvlan = mac[2]
				macinterface = mac[3]
			if 'cisco_nxos' in sshl2type:
				macaddress = mac[1]
				macvlan = mac[0]
				macinterface = mac[6]
			if 'hp' in sshl2type:
				macaddress = mac[0]
				macvlan = mac[2]
				macinterface = mac[1]
			macaddress = macaddress.encode('ascii','ignore')
			macaddress = macaddress.replace ('-','')
			macaddress = macaddress.replace ('.','')
			for ipadd in l3arptablefull:
				if 'cisco_ios' in sshl3type:
					arpmac = ipadd[2]
					arpip = ipadd[0]
					arpint = ipadd[4]
				if 'cisco_xe' in sshl3type:
					arpmac = ipadd[2]
					arpip = ipadd[0]
					arpint = ipadd[4]
				if 'cisco_nxos' in sshl3type:
					arpmac = ipadd[2]
					arpip = ipadd[0]
					arpint = ipadd[3]
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
		writer.writerow({'mac_add': 'Options: IgnoreInterfacesOver3MAC:[' + l2uplinkq.upper() + '] Options IgnoredVLANs:[' + l2ignorevlanq.upper() + ']'})
		if "Y" in l2healthcheckq.upper():
			print '---------------------------------------------------------'
			print 'Health Check Detected, starting Interface Health Check'
			writer.writerow({'mac_add': 'Health Check Information'})
			for l2health in l2healthtablefull:
				if 'cisco_xe' in sshl2type:
					l2healthport = l2health[0]
					l2healtherror = l2health[2]
					l2healtherrornumber = int(l2healtherror)
				if l2healtherrornumber > 0:
					print 'Interface: ' + l2healthport + ' is showing CRC errors, please check duplexing settings'
				else:
					print 'Interface: ' + l2healthport + ' is showing NO ERRORS'
				writer.writerow({'mac_add': 'HealthCheck' , 'mac_vlan': 'CRC Errors: ' + l2healtherror , 'mac_int': l2healthport})
			print 'Health Check Completed. If no interfaces are listed, no errors were found'
			print 'If you believe that the interfaces listed have been corrected, please clear counters on those interfaces'
else:
	for mac in l2mactablefull:
		if 'cisco_ios' in sshl2type:
			macaddress = mac[0]
			macvlan = mac[2]
			macinterface = mac[3]
		if 'cisco_xe' in sshl2type:
			macaddress = mac[0]
			macvlan = mac[2]
			macinterface = mac[3]
		if 'cisco_nxos' in sshl2type:
			macaddress = mac[1]
			macvlan = mac[0]
			macinterface = mac[6]
		if 'hp' in sshl2type:
			macaddress = mac[0]
			macvlan = mac[2]
			macinterface = mac[1]
		macaddress = macaddress.encode('ascii','ignore')
		macaddress = macaddress.replace ('-','')
		macaddress = macaddress.replace ('.','')
		for ipadd in l3arptablefull:
			if 'cisco_ios' in sshl3type:
				arpmac = ipadd[2]
				arpip = ipadd[0]
				arpint = ipadd[4]
			if 'cisco_xe' in sshl3type:
				arpmac = ipadd[2]
				arpip = ipadd[0]
				arpint = ipadd[4]
			if 'cisco_nxos' in sshl3type:
				arpmac = ipadd[2]
				arpip = ipadd[0]
				arpint = ipadd[3]
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
	print 'End of Lookup and Compare'
	print 'Additional Options: IgnoreInterfacesOver3MAC:[' + l2uplinkq.upper() + '] Options IgnoredVLANs:[' + l2ignorevlanq.upper() + ']'
	if "Y" in l2healthcheckq.upper():
		print '---------------------------------------------------------'
		print 'Health Check Detected, starting Interface Health Check'
		for l2health in l2healthtablefull:
			if 'cisco_xe' in sshl2type:
				l2healthport = l2health[0]
				l2healtherror = l2health[2]
				l2healtherrornumber = int(l2healtherror)
			if l2healtherrornumber > 0:
				print 'Interface: ' + l2healthport + ' is showing CRC errors, please check duplexing settings'
			else:
				print 'Interface: ' + l2healthport + ' is showing NO ERRORS'
		print 'Health Check Completed. If no interfaces are listed, no errors were found'
		print 'If you believe that the interfaces listed have been corrected, please clear counters on those interfaces'
print '---------------------------------------------------------'
print 'Cleaning up'
try:
	fsmmactemplatefile.close()
	os.remove('fsmmactemplate.fsm')
except:
	print 'Please manually remove the temporary file fsmmactemplate.fsm'
try:
	fsmarptemplatefile.close()
	os.remove('fsmarptemplate.fsm')
except:
	print 'Please manually remove the temporary file fsmarptemplate.fsm'
try:
	fsmhealthtemplatefile.close()
	os.remove('fsmhealthtemplate.fsm')
except:
	print 'Please manually remove the temporary file fsmhealthtemplate.fsm'

###for name in dir():
###	if not name.startswith('_'):
###		del globals()[name]
print '---------------------------------------------------------'
print 'Script Complete'