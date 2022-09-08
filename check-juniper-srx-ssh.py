# rewrite of SRX test in python, perl one doesnt work! for me
#
# DuncanRobertson 09-06-2015
#
# 8 September 2022 
# port to Python3 2022 as Python2 deprecated
# ssh_key as cli param now
#
# ssh user on the Juniper works as User Class read-only
#

import paramiko

import sys

try:
   ssh_key_filename = sys.argv[1]
   check = sys.argv[2]
   host = sys.argv[3]
   user = sys.argv[4]
except:
   print("simple nagios check to check Juniper SRX via ssh, needs passwordless public key ssh set up")
   print("usage: %s ssh-priv-key [alarms|environment] hostname username" % sys.argv[0])

if check not in ["alarms","environment"]:
   print("parameter2 check type must be either alarms or environment")
   sys.exit(1)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
   ssh.connect(host,22 ,user,allow_agent=True,key_filename=ssh_key_filename)
except Exception as  e:
   print("Error with ssh to ",host,e)
   sys.exit(2)

if check == "alarms":
   stdin,stdout,stderr = ssh.exec_command('show chassis alarms')

   output = stdout.read()
   if output.find(b'No alarms currently active') > -1:
      print("OK",output.strip())
      sys.exit(0)
   else:
      print("ALERT:",output.strip())
      sys.exit(2)

if check == "environment":
   stdin,stdout,stderr = ssh.exec_command('show chassis environment')

   envlines = stdout.readlines()
   # ignore first line, its a heading
   badenvlines = ""
   for envline in envlines[1:]:
      # either we need an OK or Absent for not installed, otherwise gather it as an alert
      if envline.find('OK') > -1 or envline.find('Absent') > -1:
         pass
      else:
         badenvlines = badenvlines + " " + envline.strip()
   if not badenvlines == "":
      print("CRITICAL: ",badenvlines)
      sys.exit(2)
   print("OK")
   sys.exit(0)


print("CODE ERROR shouldnt have got here.")
sys.exit(1)
