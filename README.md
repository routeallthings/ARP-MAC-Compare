# MAC to ARP Comparison Tool

The goal of this project was to create an easy to use script that will take a L2 switch and compare it against a L3 arp table to ensure that all the MAC addresses have an associated IP address. The primary use case would be switch migration from one to the next to ensure correct port placement of wires.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Netmiko (https://github.com/ktbyers/netmiko)
You can install this with pip via "pip install netmiko"
TextFSM (https://github.com/google/textfsm)
You can install this with pip via "pip install textfsm"

## Deployment

Just execute the script and answer the questions

## Built With

* Netmiko (https://github.com/ktbyers/netmiko) - Thanks Kirk Byers for the excellent library

## Features
- Mac Address Lookup
- ARP Lookup
- Export to CSV

## *Caveats
- Have not tested HP Comware
- Only works with groups of the same switches (Layer 2 groups are separate from Layer 3 groups)

## Versioning

Version 1.0 - Created initial copy of tool

## Authors

* **Matt Cross** - [RouteAllThings](https://github.com/routeallthings)

See also the list of [contributors](https://github.com/routeallthings/ARP-MAC-Compare/contributors) who participated in this project.

## License

This project is licensed under the GNU - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to HBS for giving me a reason to write this.
