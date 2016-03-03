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
def main():
  
  #parse command line options
  (options,args)=parseOptions()

  expectedMinions=args
  
  maxAttempts=100
  timeToWaitBetweenAttempts=2
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
    cmd=["sudo","salt","\'*\'","state.highstate"]
    process=Popen(cmd,stdout=PIPE,stderr=PIPE)
    stdout,stderr=process.communicate()
    print(stdout)
    #print(stderr)
  else:
    print("Not all expected minions present after "+str(maxAttempts)
      +" checks every "+str(timeToWaitBetweenAttempts)+" seconds. Not "
      +"executing \"salt '*' state.highstate\". Check that all expected "
      +"minions are present with \"salt-run manage.up\" command.")
 
if __name__ == "__main__":
  main()