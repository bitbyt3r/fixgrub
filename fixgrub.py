#!/usr/bin/python
import os
import shutil

GRUB_CONF = "/boot/grub/grub.conf"
BACKUP_FILE = "/boot/grub/grub.conf.old"
TMP_FILE = "/tmp/menu.lst.tmp"

with open(GRUB_CONF, "r") as confFile:
  conf = confFile.read()
sections = conf.split("title")
header = sections[0]
osSections = sections[1:]

newHeader = ""
for i in header.split("\n"):
  if "default" in i:
    newHeader += "default=0\n"
  else:
    newHeader += i+"\n"
newHeader = newHeader.strip()
osSections = ["title "+x.strip() for x in osSections]

redhatKernels = []
openvzKernels = []
for i in osSections:
  for j in i.split("\n"):
    if "title" in j:
      if "Red Hat" in i:
        redhatKernels.append(j.split("(")[1].split(")")[0])
      elif "OpenVZ" in i:
        openvzKernels.append(j.split("(")[1].split(")")[0])

redhatKernelsSorted = []
for i in redhatKernels:
  version = i.split("-")[0].split(".")+i.split("-")[1].split(".")
  redhatKernelsSorted.append(version)
redhatKernelsSorted.sort()
for i in redhatKernelsSorted:
  i[2] += "-"+i[3]
  i.pop(3)
redhatKernelsSorted = [".".join(x) for x in redhatKernelsSorted]
redhatKernelsSorted.reverse()
for i in xrange(len(redhatKernelsSorted)):
  if "debug" in redhatKernelsSorted[i]:
    redhatKernelsSorted.append(redhatKernelsSorted.pop(i))

openvzKernelsSorted = []
for i in openvzKernels:
  version = i.split("-")[0].split(".")
  version.append(i.split("-")[1])
  openvzKernelsSorted.append(version)
openvzKernelsSorted.sort()
for i in openvzKernelsSorted:
  i[2] += "-"+i[3]
  i.pop(3)
openvzKernelsSorted = [".".join(x) for x in openvzKernelsSorted]
openvzKernelsSorted.reverse()
for i in xrange(len(openvzKernelsSorted)):
  if "debug" in openvzKernelsSorted[i]:
    openvzKernelsSorted.append(openvzKernelsSorted.pop(i))

finalSections = []
for i in openvzKernelsSorted:
  for j in osSections:
    if "("+i+")" in j:
      finalSections.append(j)
for i in redhatKernelsSorted:
  for j in osSections:
    if "("+i+")" in j:
      finalSections.append(j)
for i in osSections:
  if "Windows" in i:
    finalSections.append(i)
  
with open(TMP_FILE, "w") as temp:
  temp.write(newHeader+"\n")
  for i in finalSections:
    temp.write(i+"\n")

if os.system("diff "+TMP_FILE+" "+GRUB_CONF):
  shutil.copy(GRUB_CONF, BACKUP_FILE)
  shutil.copy(TMP_FILE, GRUB_CONF)
