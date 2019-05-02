![SSHA](https://i.imgur.com/LOFpfJ8.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

### About:
SSH Alias is a program for Linux users to easily connect to all your SSH servers. 
Add, edit, and remove aliases to connect to so that you never have to remember the hostname/IP, port, key file location and other various settings while connecting via SSH.

### Features:
  - Saves SSH configurations as aliases
  - Remembers key locations and other SSH options
  - Supports SSH+Mosh
  - Tests latency of your SSH connection
  - Connects with alias name on shell
  - Command line interface for adding, editing and removing aliases

### Latest Version:
* v1.0

### Installation:

SSH Alias requires [Python](https://www.python.org/downloads/) v3+, SSH and Linux to run.

Install on entire system:
```bash
git clone https://github.com/jordanhillis/ssha.git
cd ssha
sudo pip3 install -r requirements.txt
sudo cp ssha.py /usr/bin/ssha
sudo chmod a+x /usr/bin/ssha
ssha
```
Install for single user:
```bash
git clone https://github.com/jordanhillis/ssha.git
cd ssha
pip3 install -r requirements.txt
mkdir ~/.ssh
cp ssha.py ~/.ssh/ssha
chmod a+x ~/.ssh/ssha
echo "alias ssha='~/.ssh/ssha'" >> ~/.bashrc
ssha
```

### Usage:

| SSHA Internal Commands | About |
| ------ | ------ |
| c,conn,connect ALIAS | Connect to a configured alias|
| a,add ALIAS | Add an alias to use for connections |
| e,edit ALIAS | Edit an already configured alias |
| d,del,delete,rm ALIAS | Remove an alias from the connection list |
| l,ls,list | List all the configured alias connections |
| q,exit,quit | Exit the program | 
| h,help | Display help screen |

To quickly connect to a preconfigured alias you can run the command
```bash
ssha SERVERNAME
```
Replace SERVERNAME with the name of the alias that you would like to connect to.

### Example Usage:
##### Adding an alias
![Adding alias](http://i.imgur.com/AVgECIH.png)

##### Alias list
![Alias list](http://i.imgur.com/UIJQDMI.png)

##### Connecting to an alias
![Connecting to alias](http://i.imgur.com/uj5OVJ8.png)

##### Quick connect to an alias via shell
![Quick connect to alias](https://i.imgur.com/kmNhgES.png)

### Developers:
 - Jordan Hillis - *Lead Developer*

### License:
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

