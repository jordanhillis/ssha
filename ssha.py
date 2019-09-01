#!/usr/bin/env python3
import subprocess, os, signal, sys, time, socket
from tinydb import TinyDB, Query, where
from sys import platform

'''
______________________________________________
                   SSH Alias
               By Jordan Hillis
              jordan@hillis.email
           https://jordanhillis.com
______________________________________________
MIT License
Copyright (c) 2019 Jordan S. Hillis
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
______________________________________________
'''

# Version number
version = "1.0"

# Class for coloring different events 
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	INPUT = '\033[1m\033[92m'


# Verify the user is running Linux
if platform not in ["linux","linux2","darwin"]:
	print(bcolors.FAIL + "Sorry, this program only supports Linux at this time..." + bcolors.ENDC)
	exit(0)


# See if .ssh exists in home directory, if not create it
ssh_path = os.path.expanduser("~/.ssh")
try:
	os.makedirs(ssh_path)
except FileExistsError:
	pass


# Database to use for storing the alias connections
db = TinyDB(ssh_path+"/ssha.json")


# Function to detect force close
def ctrl_c(siganl, frame):
	print(bcolors.BOLD + bcolors.OKGREEN + "\n<< Goodbye!" + bcolors.ENDC)
	# Exit script successfully
	exit(0)


# Detect sigint sent
signal.signal(signal.SIGINT, ctrl_c)


# Input but with pre defined values. Used for aliasEdit below
def inputChange(prompt, default):
	bck = chr(8) * len(default)
	# Display input but with default value
	ret = input(prompt + default + bck)
	return ret or default


# Check if alias exists
def rowExist(alias):
	# Search alias in database
	row = db.search(where('alias') == alias)
	if not row:
		return False
	else:
		return True


# Delete alias from database
def aliasDelete(inputCmd):
	try:
		# Gather alias from 2nd argument passed
		alias_name = inputCmd[1].lower()
		# Check if alias exists
		if rowExist(alias_name):
			# Prompt user to confirm if they want the alias deleted
			del_alias_q = input(bcolors.WARNING + "Delete the alias " + alias_name.upper() + "? (y/n): " + bcolors.ENDC)
			# Delete alias upon y being entered
			if del_alias_q.lower() == "y":
				# Notify the deletion of the alias and remove it from the database
				print(bcolors.WARNING + "<< Alias " + alias_name.upper() + " has been deleted successfully!" + bcolors.ENDC)
				db.remove(where('alias') == alias_name)
				# Display all the aliases
				aliasList()
		# If the alias doesn't exist
		else:
			print(bcolors.FAIL + "The alias " + alias_name.upper() + " does not exist" + bcolors.ENDC)
	# Catch all for errors, usually this will be no alias specified
	except Exception:
		print(bcolors.FAIL + "You need to enter an alias that you want to delete" + bcolors.ENDC)


# Connect to a given alias
def aliasConnect(inputCmd):
	try:
		# Gather alias from 2nd argument passed
		alias_name = inputCmd[1].lower()
		# Check if the alias exists
		if rowExist(alias_name):
			# Find alias row in database
			for row in db.search(where('alias') == alias_name):
				print(bcolors.WARNING + "<< Connecting to alias " + row["alias"].upper() + " using SSH" + ("+Mosh " if row["mosh"] else " ") + row["user"] + "@" + row["hostname"] + ":" + row["port"] + "...", end="")
				# Check if mosh is installed
				if row["mosh"]:
					if subprocess.call(['which', 'mosh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
						print(bcolors.FAIL + "ERROR")
						print("Mosh is not installed on your system..." + bcolors.ENDC)
						exit(0)
				# Check if mosh is installed
				if subprocess.call(['which', 'ssh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
					print(bcolors.FAIL + "ERROR")
					print("SSH is not installed on your system..." + bcolors.ENDC)
					exit(0)
				# Start creating the SSH command to be passed to the system
				sshCmd = row["user"] + "@" + row["hostname"] + " -p " + row["port"] + " "
				if row['mosh']:
					sshCmd = "mosh " + sshCmd.replace(" -p", " --ssh=\"ssh -p")
				else:
					sshCmd = "ssh " + sshCmd
				if row['key']:
					# Check if the key exists
					if os.path.exists(row['key']):
						sshCmd += "-i " + row['key']
					# Key does not exist
					else:
						print(bcolors.FAIL + "ERROR\nThe key you have specified does not exist...\nPlease double check your path to this file" + bcolors.ENDC)
						break
				if row['options']:
					sshCmd += " " + row['options']
				if row['mosh'] == "True":
					sshCmd += "\""
				# Check if SSH server is alive
				try:
					# Create socket for checking alive status
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.settimeout(10)
					start_time = time.time()
					# Check if SSH server is alive
					alive_status = s.connect_ex((row["hostname"], int(row["port"])))
					s.close()
					# Measure latency of socket
					latency = float(round((time.time()-start_time)*1000,2))
					if alive_status == 0:
						print(bcolors.OKGREEN + "SUCCESS" + bcolors.ENDC)
						print(bcolors.OKGREEN + "Current latency for " + row["hostname"] + " is ", end="")
						# Grade their latency
						if latency < 100:
							print("low", end="")
						elif latency < 200:
							print("moderate", end="")
						else:
							print("high", end="")
						print(" at " + str(latency) + " ms" + bcolors.ENDC)
						# Connect to SSH server
						os.system(sshCmd)
						print(bcolors.WARNING + "\n<< Disconnected from alias " + alias_name.upper() + bcolors.ENDC)
					# SSH server is dead
					else:
						print(bcolors.FAIL + "FAILURE" + bcolors.ENDC)
						print(bcolors.FAIL + "Cannot make a successful connection to " + alias_name + ".\nPlease check your network connection and the SSH server." + bcolors.ENDC)
				# Catch all for errors, usually this would be that the hostname or port are invalid
				except Exception:
					print(bcolors.FAIL + "FAILURE" + bcolors.ENDC)
					print(bcolors.FAIL + "Alias " + alias_name + " seems to have some connection errors..." + bcolors.ENDC)
		# The alias given doesn't exist
		else:
			print(bcolors.FAIL + "That alias does not exist..." + bcolors.ENDC)
	# Catch all for error, typically that they did not pass an alias after the connect command
	except Exception:
		print(bcolors.FAIL + "You need to enter an alias that you want to connect to" + bcolors.ENDC)


# Edit configured aliases
def aliasEdit(inputCmd):
	try:
		# Gather alias from 2nd argument passed
		alias_name = inputCmd[1].lower()
		# Check if alias exists
		if rowExist(alias_name):
			# Get the row from the database
			for row in db.search(where('alias') == alias_name):
				# Ask the user to configure each setting below
				edit_alias = inputChange("Alias Name: ", row["alias"]).lower()
				edit_user = inputChange("SSH User: ", row["user"])
				edit_hostname = inputChange("SSH Hostname/IP: ", row["hostname"])
				edit_port = inputChange("SSH Port: ", row["port"])
				edit_mosh_q = inputChange("Use Mosh? (y/n): ", "y" if row["mosh"] else "n")
				if edit_mosh_q.lower() == "y":
					edit_mosh = "True"
				else:
					edit_mosh = ""
				edit_key_q = inputChange("Key-based authentication? (y/n): ", "y" if row["key"] else "n")
				if edit_key_q.lower() == "y":
					edit_key = inputChange("SSH Key Location: ", row["key"])
				else:
					edit_key = ""
				edit_options_q = inputChange("Other options to use?: ", "y" if row["options"] else "n")
				if edit_options_q.lower() == "y":
					print("Example options: -c aes128 -C")
					edit_options = inputChange("SSH Options: ", row["options"])
				else:
					edit_options = ""
				# Notify the user and update the database with the updated information for the alias
				print(bcolors.WARNING + "<< Alias " + edit_alias + " has been updated successfully!" + bcolors.ENDC)
				db.update({
					'alias': edit_alias,
					'user': edit_user,
					'hostname': edit_hostname,
					'port': edit_port,
					'mosh': edit_mosh,
					'key': edit_key,
					'options': edit_options
					}, 
					where('alias') == row['alias']
				)
				# Display the alias list
				aliasList()
		# Alias doesn't exist
		else:
			print(bcolors.FAIL + "That alias does not exist..." + bcolors.ENDC)
	# Catch all for errors, typically the user did not specify an alias after the edit command
	except Exception:
		print(bcolors.FAIL + "You need to enter an alias that you want to edit" + bcolors.ENDC)


# Add aliases to the database
def aliasAdd(inputCmd):
	try:
		# Gather the alias from the given input
		alias_name = inputCmd[1].lower()
		# Check if the alias alreadyt exists
		if rowExist(alias_name):
			print(bcolors.FAIL + "That alias already exists..." + bcolors.ENDC)
		# Alias does not exist, can continue with adding
		else:
			# Configure the alias settings below
			print(bcolors.WARNING + "Alias Name: " + alias_name + bcolors.ENDC)
			add_user = input("SSH User: ")
			add_hostname = input("SSH Hostname/IP: ")
			add_port = input("SSH Port: ")
			add_mosh_q = input("Use Mosh? (y/n): ")
			if add_mosh_q.lower() == "y":
				add_mosh = "True"
			else:
				add_mosh = ""
			add_key_q = input("Key-based authentication? (y/n): ")
			if add_key_q.lower() == "y":
				add_key = input("SSH Key Location: ")
			else:
				add_key = ""
			add_options_q = input("Other options to use?: ")
			if add_options_q.lower() == "y":
				print("Example options: -c aes128 -C")
				add_options = input("SSH Options: ")
			else:
				add_options = ""
			# Notify the user and add the alias to the database 
			print(bcolors.WARNING + "<< Alias " + alias_name + " has been added successfully!" + bcolors.ENDC)
			db.insert({
				'alias': alias_name,
				'user': add_user, 
				'hostname': add_hostname,
				'port': add_port,
				'mosh': add_mosh,
				'key': add_key,
				'options': add_options
			})
			# Display the alias list
			aliasList()
	# Catch all for errors, typically the user did not specify an alias name after the add command
	except Exception:
		print(bcolors.FAIL + "You need to enter an alias that you want to add" + bcolors.ENDC)


# Display help screen for given usage and examples
def aliasHelp():
	print("\n  " + bcolors.UNDERLINE + bcolors.HEADER + "COMMANDS:" + bcolors.ENDC)
	print(bcolors.BOLD + "  c,conn,connect ALIAS" + bcolors.ENDC + "    - Connect to a configured alias")
	print("                            + Example usage: >> " + bcolors.OKGREEN + "conn server1" + bcolors.ENDC)
	print(bcolors.BOLD + "  a,add ALIAS" + bcolors.ENDC + "             - Add an alias to use for connections")
	print("                            + Example usage: >> " + bcolors.OKGREEN + "add server1" + bcolors.ENDC)
	print(bcolors.BOLD + "  e,edit ALIAS" + bcolors.ENDC + "            - Edit an already configured alias")
	print("                            + Example usage: >> " + bcolors.OKGREEN + "edit server1" + bcolors.ENDC)
	print(bcolors.BOLD + "  d,del,delete,rm ALIAS" + bcolors.ENDC + "   - Remove an alias from the connection list")
	print("                            + Example usage: >> " + bcolors.OKGREEN + "del server1" + bcolors.ENDC)
	print(bcolors.BOLD + "  l,ls,list" + bcolors.ENDC + "               - List all the configured alias connections")
	print("                            + Example usage: >> " + bcolors.OKGREEN + "ls" + bcolors.ENDC)
	print(bcolors.BOLD + "  q,exit,quit" + bcolors.ENDC + "             - Exit the program")
	print("                            + Example usage: >> " + bcolors.OKGREEN + "exit" + bcolors.ENDC)
	print(bcolors.BOLD + "  h,help" + bcolors.ENDC + "                  - Display this help screen")
	print("                            + Example usage: >> " + bcolors.OKGREEN + "help" + bcolors.ENDC)
	print("\n  " + bcolors.UNDERLINE + bcolors.HEADER + "Quick connect to an alias:" + bcolors.ENDC)
	print("  Example usage: " + sys.argv[0] + " server1\n")


# List the aliases in the database
def aliasList():
	rowNum = 1
	# Loop through each alias
	for row in db.all():
		if rowNum == 1:
			# Show column headers
			print(bcolors.HEADER + bcolors.BOLD + "\n      #:    ALIAS:       TYPE:        SERVER:                    " + bcolors.ENDC)
		for i in range(3-len(str(rowNum))):
			print(" ", end="")
		print("   [" + str(rowNum) + "]    ", end="")
		print(bcolors.BOLD + bcolors.WARNING + row["alias"].upper() + bcolors.ENDC + bcolors.BOLD, end="")
		# Format the spaces between the alias name and the SSH column to align
		for i in range(12-len(row["alias"])):
			print(" ", end="")
		# Show if it using Mosh
		if row["mosh"]:
			print(" [" + bcolors.OKBLUE + "SSH+Mosh" + bcolors.ENDC + bcolors.BOLD +"]", end="")
			# Format the spacing
			for i in range(3):
				print(" ", end="")
		# Regular SSH connection
		else:
			print(" [" + bcolors.OKBLUE + "SSH" + bcolors.ENDC + bcolors.BOLD + "]", end="")
			# Format the spacing
			for i in range(8):
				print(" ", end="")
		print("[" + bcolors.OKGREEN + row["hostname"] + ":" + row["port"] + bcolors.ENDC + bcolors.BOLD + "]" + bcolors.ENDC)
		rowNum += 1
	# There is no connections saved, display the help menu to get them started
	if rowNum == 1:
		aliasHelp()
	else:
		print("")


# Main menu
def main():
	# Quick connect
	try: 
		# Check if the alias was passed in sys arg
		if sys.argv[1]:
			inputCommand = ["",sys.argv[1]]
			# Catch -h and --help argv[1]
			if sys.argv[1] in ["-h","--help"]:
				print("\n  Run " + sys.argv[0] + " to run these commands within the program.")
				aliasHelp()
				exit(0)
			else:
				# Attempt to connect to the alias 
				aliasConnect(inputCommand)
				# Exit upon completion of connection
				exit(0)
	except Exception:
		pass
	# Display header and author description
	print(bcolors.BOLD + bcolors.OKGREEN + "  ____ ____ _  _    ____ _    _ ____ ____")
	print("  [__  [__  |__|    |__| |    | |__| [__ ")
	print("  ___] ___] |  |    |  | |___ | |  | ___]" + bcolors.ENDC)
	print(bcolors.OKBLUE + "\n  v" + version + " by Jordan Hillis [jordan@hillis.email]" + bcolors.ENDC)
	print("____________________________________________________")             
	# List all the aliases
	aliasList()
	# Ask the user for a command
	print("Type your command below (enter h or help)")
	while True:
		inputCommand = input(bcolors.INPUT + ">> " + bcolors.ENDC).split()
		try:
			command1 = inputCommand[0].lower()
			# Connect to alias command
			if command1 in ["c","conn","connect"]:
				aliasConnect(inputCommand)
			# Edit alias command
			elif command1 in ["e","edit"]:
				aliasEdit(inputCommand)
			# Delete alias command
			elif command1 in ["d","del","delete","rm"]:
				aliasDelete(inputCommand)
			# Add alias command
			elif command1 in ["a","add"]:
				aliasAdd(inputCommand)
			# Help command
			elif command1 in ["h","help","?"]:
				aliasHelp()
			# List all alias command
			elif command1 in ["l","ls","list"]:
				aliasList()
			# Exit script command
			elif command1 in ["exit","quit","q"]:
				print(bcolors.BOLD + bcolors.OKGREEN + "<< Goodbye!" + bcolors.ENDC)
				exit(0)
			# See if the user got confused and tried to execute the python file inside our command line
			elif ".py" in command1:
				print(bcolors.FAIL + "You need to exit this command line (CTRL+C) and then enter\nthat command in the regular shell interface" + bcolors.ENDC)
				exit(0)
			# Invalid command entered
			else:
				print(bcolors.FAIL + "Invalid command. Type h or help for command line usage" + bcolors.ENDC)
		except Exception:
			pass


main()
