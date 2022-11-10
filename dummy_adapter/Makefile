#
# Makefile for the kernel dvr_dmx device drivers.
#

dvb_dummy-objs := dvb_dummy_adapter.o
obj-m := dvb_dummy.o

# Ubuntu
KDIR := /usr/src/linux-headers-`uname -r`

# Fedora
#KDIR := /usr/src/kernels/`uname -r`

modules:
	make -C $(KDIR) SUBDIRS=$(PWD) modules

clean:
	make -C $(KDIR) SUBDIRS=$(PWD) clean

EXTRA_CFLAGS += -Idrivers/media/dvb/dvb-core -Idrivers/media/dvb/frontends -Idrivers/media/dvb-core -Idrivers/media/dvb-frontends
