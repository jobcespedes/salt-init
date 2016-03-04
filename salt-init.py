#!/usr/bin/env python
from __future__ import print_function
from subprocess import Popen, PIPE
import time
import optparse as op

def parseOptions():
  """Parses command line options
  
  """
  
  parser=op.OptionParser(usage="Usage: %prog [options] EXPECTEDMINIONS"
    ,version="%prog 1.0",description="waits for all expected minions to connect"
    +" then then provisions them with salt")
  
  #parse command line options
  return parser.parse_args()
#def isStrAnIp(string):
#  pattern=re.compile("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}")
#  return pattern.match(string)
def main():
  
  #parse command line options
  (options,args)=parseOptions()
  
  #minionIps=[]
  #minionHostNames=[]
  #for arg in args:
  #  if isStrAnIP(arg):
  #    minionIps.append(arg)
  #  else: 
  #    minionHostNames.append(arg)
      
  #check that minion host names and IPs are the same length
  #if len(minionIPs)!=len(minionHostNames):
  #  raise Exception("Do not have same number of minion IPs "+str(minionIPS)
  #    +" as minion host names "+str(minionHostNames))
  
  expectedMinions=args
  
  #TODO: try pinging each minion => I can't get the ip-address before the 
  #machines are booted (i.e. when I inject the cloudInit script). Which means if
  #I wanted to get the ips here, I would have to query them here using the 
  #OpenStack python API, which would then require the OpenStack rc file and 
  #password... arg.
  
  maxAttempts=100
  timeToWaitBetweenAttempts=10
  count=0
  allMinionsPresent=False
  cmd=["sudo","salt-run","manage.up"]
  while not allMinionsPresent and count<maxAttempts:
    
    #get list of salt minions
    process=Popen(cmd,stdout=PIPE,stderr=PIPE)
    stdout,stderr=process.communicate()
    namestemp=stdout.split()
    minions=[]
    for name in namestemp:
      if name!="-":
        minions.append(name)
    
    #see if all expected minions present
    allMinionsPresent=True
    for expectedMinion in expectedMinions:
      if expectedMinion not in minions:
        allMinionsPresent=False
    
    #increment count
    count+=1
    
    #wait a little bit
    time.sleep(timeToWaitBetweenAttempts)
  
  if(allMinionsPresent):
  
    #create a list of minions
    minonsString="\'"
    for i in range(len(expectedMinions)-1):
      minonsString+=expectedMinions[i]+","
    minonsString+=expectedMinions[len(expectedMinions)-1]+"\'"
    
    print("All minions present, sending command to go to highstate")
    
    #run high state command
    cmd=["sudo","salt","-L",minonsString,"state.highstate"]
    process=Popen(cmd,stdout=PIPE,stderr=PIPE)
    stdout,stderr=process.communicate()
    print(stdout)
    #print(stderr)
    
    #TODO: should also now disable accept all keys as we have all that we want
  else:
    #TODO: seems even failed ssh's into missing minions allows them to suddenly 
    #be detected, maybe I should try pining them
    print("Not all expected minions present after "+str(maxAttempts)
      +" checks every "+str(timeToWaitBetweenAttempts)+" seconds. Not "
      +"executing \"salt '*' state.highstate\". Check that all expected "
      +"minions are present with \"salt-run manage.up\" command.")
 
if __name__ == "__main__":
  main()