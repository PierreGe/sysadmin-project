#!/usr/bin/python
#-*-coding:utf8-*

import sys

class Parser(object):
  def __init__(self, string):
    self.string = string.split('\n')
    self.columnName = ["CONTAINER ID", "IMAGE", "COMMAND", "CREATED", "STATUS", "PORTS", "NAMES"]
    self.indexes = [self.string[0].index(columnName) for columnName in self.columnName]

  def parse(self):
    self.data = []
    for row in self.string[1:]:
      r = []
      for i in range(len(self.columnName)-1):
        r.append(row[self.indexes[i]:self.indexes[i+1]].strip())
      r.append(row[self.indexes[-1]:].strip())
      self.data.append(r)
      
  def getPort(self,string):
    i = string.find("->")
    if i==-1:
      return None
    j=i-1
    while string[j]!=':':
      j-=1
    k=i+2
    while string[k]!='/':
      k+=1
    return (string[i+2:k],string[j+1:i])

  def format(self):
    print('<table>')
    print('<tr>')
    for c in self.columnName:
      print('<th>{0}</th>'.format(c))
    print('<th>TOGGLE</th>')
    print('<th>DUPLICATE</th>')
    print('<th>DELETE</th>')
    print('</tr>')
    for row in self.data:
      print('<tr>')
      port = self.getPort(row[-2])
      if (port!=None):
        print('<td><a href="http://supayr.ninja:{1}" target="_blank">{0}</a></td>'.format(row[0],port[1]))
      else:
        print('<td>{0}</td>'.format(row[0]))
        
      for cellContent in row[1:-2]:
        print('<td>{0}</td>'.format(cellContent))
      print('<td>')
      print('  <form method="post" action="docker_handler.cgi">')
      print('    <input type="text" name="newPort" value="{0}" defaultValue="{0}" port="{1}" onfocus="this.style.border=\'1px solid lightgrey\'; this.style.background=\'white\'; this.value=this.getAttribute(\'port\')" onblur="this.style.border=\'none\'; this.style.background=\'transparent\'; if (this.value!=this.getAttribute(\'port\')) this.form.submit(); else this.value=this.getAttribute(\'defaultValue\');" >'.format(row[-2],port[1]+":"+port[0] if port!=None else ''))
      print('    <input type="hidden" name="serviceId" value="{0}">'.format(row[0]))
      print('    <input type="hidden" name="imageName" value="{0}">'.format(row[1]))
      print('  </form>')
      print('</td>')
      print('<td>')
      print('  <form method="post" action="docker_handler.cgi">')
      print('    <input type="text" name="newName" value="{0}" onfocus="this.style.border=\'1px solid lightgrey\'; this.style.background=\'white\'" onblur="this.style.border=\'none\'; this.style.background=\'transparent\'; if (this.value!=this.form.oldName.value) this.form.submit()" >'.format(row[-1]))
      print('    <input type="hidden" name="oldName" value="{0}">'.format(row[-1]))
      print('  </form>')
      print('</td>')
      print('<td>')
      print('  <form method="post" action="docker_handler.cgi">')
      print('    <label class="switch">')
      print('      <input type="checkbox" class="switch-input" onclick="this.form.submit();" {0}>'.format("checked" if "Up" in row[4] else ""))
      print('      <input name="toggleService" type="hidden" value="{0}">'.format(row[0]))
      print('      <span data-off="Off" data-on="On" class="switch-label"></span>')
      print('      <span class="switch-handle"></span>')
      print('    </label>')
      print('  </form>')
      print('</td>')
      print('<td>')
      print('  <form method="post" action="docker_handler.cgi">')
      print('    <input type="button" onclick="this.form.submit();" value="Duplicate/Fork" id="duplicate-button-{0}">'.format(row[0]))
      print('    <input name="duplicate" type="hidden" value="{0}">'.format(row[0]))
      print('    <input name="name" type="hidden" value="{0}">'.format(row[-1]))
      print('  </form>')
      print('</td>')
      print('<td>')
      print('  <form method="post" action="docker_handler.cgi">')
      print('    <input type="button" onclick="this.form.submit();" value="Delete" id="delete-button-{0}">'.format(row[0]))
      print('    <input name="delete" type="hidden" value="{0}">'.format(row[0]))
      print('  </form>')
      print('</td>')
      
      print('</tr>')
      
    print('</table>')

def main():
  p = Parser(sys.argv[1])
  p.parse()
  p.format()

if __name__=="__main__":
  main()
