import re

def end_form(s,start):
 depth=0;quoted=False;esc=False
 for i in range(start,len(s)):
  c=s[i]
  if quoted:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return i+1
 raise ValueError('unbalanced')

def footprint_spans(s):
 for m in re.finditer(r'^\t\(footprint ',s,re.M):
  start=m.start();end=end_form(s,s.index('(',start));chunk=s[start:end]
  ref=re.search(r'\(property "Reference" "([^"]*)"',chunk)[1]
  uuid=re.search(r'^\t\t\(uuid "([^"]+)"',chunk,re.M)[1]
  yield ref,uuid,start,end,chunk

def subforms(s,head):
 return [s[m.start():end_form(s,m.start())] for m in re.finditer(r'\('+head+r'\s',s)]
