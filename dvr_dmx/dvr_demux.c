/*
 * SOURCE CODE UNDER GPL.
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/delay.h>

#include "dmxdev.h"
#include "dvb_demux.h"


DVB_DEFINE_MOD_OPT_ADAPTER_NR(adapter_nr);


struct null_demux {
	struct dvb_demux dvb_demux;
	struct dmxdev dmxdev;
	struct dmx_frontend mem_frontend;

	struct dvb_adapter adapter;
};

static struct null_demux *null_dmx;

static int null_dmx_start_feed(struct dvb_demux_feed *dvbdmxfeed)
{
	return 0;
}

static int null_dmx_stop_feed(struct dvb_demux_feed *dvbdmxfeed)
{
	return 0;
}

int __init null_dmx_init(void)
{
	int err;

	null_dmx = kzalloc(sizeof(*null_dmx), GFP_KERNEL);
	if (unlikely(!null_dmx)) {
		printk(KERN_ERR "%s: Not able to alloc null_dmx struct\n", __func__);
		return -ENOMEM;
	}

	err = dvb_register_adapter(&null_dmx->adapter, "nulldemux",
				   THIS_MODULE, NULL, adapter_nr);
	if (unlikely(err))
		goto err_kfree;
	null_dmx->adapter.priv = null_dmx;

	null_dmx->dvb_demux.dmx.capabilities =
	    DMX_TS_FILTERING | DMX_SECTION_FILTERING | DMX_MEMORY_BASED_FILTERING;
	null_dmx->dvb_demux.priv = NULL;
	null_dmx->dvb_demux.filternum = 32;
	null_dmx->dvb_demux.feednum = 32;
	null_dmx->dvb_demux.start_feed = null_dmx_start_feed;
	null_dmx->dvb_demux.stop_feed = null_dmx_stop_feed;
	null_dmx->dvb_demux.write_to_decoder = NULL;

	err = dvb_dmx_init(&null_dmx->dvb_demux);
	if (err < 0) {
		printk("%s(): dvb_dmx_init failed (errno = %d)\n", __func__, err);
		dvb_unregister_adapter (&null_dmx->adapter);
		return -ENODEV;
	}

	null_dmx->dmxdev.filternum = null_dmx->dvb_demux.filternum;
	null_dmx->dmxdev.demux = &null_dmx->dvb_demux.dmx;
	null_dmx->dmxdev.capabilities = 0;

	err = dvb_dmxdev_init(&null_dmx->dmxdev, &null_dmx->adapter);
	if (err < 0) {
		printk("%s(): dvb_dmxdev_init failed (errno = %d)\n", __func__, err);
		dvb_dmx_release(&null_dmx->dvb_demux);
		dvb_unregister_adapter (&null_dmx->adapter);
		goto err_kfree;
	}

	null_dmx->mem_frontend.source = DMX_MEMORY_FE;
	null_dmx->dmxdev.demux->add_frontend(null_dmx->dmxdev.demux, &null_dmx->mem_frontend);

	printk("%s()\n", __func__);
	return 0;

err_kfree:
	printk(KERN_CRIT "%s() error\n", __func__);
	kfree(null_dmx);
	return -ENODEV;
}

void __exit null_dmx_exit(void)
{
	if (!null_dmx) {
		printk(KERN_CRIT "%s not happen!\n", __func__);
		return;
	}

	dvb_dmxdev_release(&null_dmx->dmxdev);

	dvb_unregister_adapter(&null_dmx->adapter);
	kfree(null_dmx);
	null_dmx = NULL;

	printk("%s()\n", __func__);
}

module_init (null_dmx_init);
module_exit (null_dmx_exit);

MODULE_DESCRIPTION("Null DVB Driver");
MODULE_LICENSE("GPL");
