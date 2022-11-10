#
# Makefile for the kernel dvr_dmx device drivers.
#

dvr_dmx-objs := dvr_demux.o
obj-m := dvr_dmx.o

#KDIR := /usr/src/linux-headers-2.6.38-11-generic
KDIR := /usr/src/linux-headers-`uname -r`

modules:
	make -C $(KDIR) SUBDIRS=$(PWD) modules

clean:
	make -C $(KDIR) SUBDIRS=$(PWD) clean

EXTRA_CFLAGS += -Idrivers/media/dvb/dvb-core
