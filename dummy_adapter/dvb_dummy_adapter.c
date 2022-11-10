/*
 *  Dummy DVB adapter driver
 *
 *  Copyright (C) 2010 Andy Walls <awalls@xxxxxxxxx>
 *
 *  Partially based on cx18-dvb.c driver code
 *  Copyright (C) 2008 Steve Toth <stoth@xxxxxxxxxxxxxx>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/init.h>

#include <linux/platform_device.h>

#include "dvb_demux.h"
#include "dvb_frontend.h"
#include "dvb_net.h"
#include "dvbdev.h"
#include "dmxdev.h"
#include "dvb_dummy_fe.h"

MODULE_AUTHOR("Andy Walls");
MODULE_DESCRIPTION("Dummy DVB adapter driver");
MODULE_LICENSE("GPL");
#define DVB_DUMMY_VERSION "0:0.1"
MODULE_VERSION(DVB_DUMMY_VERSION);

DVB_DEFINE_MOD_OPT_ADAPTER_NR(adapter_nr);

static int debug;

static int fe_type[DVB_MAX_ADAPTERS];
static unsigned int fe_type_c = 1;

module_param(debug, int, 0644);
module_param_array(fe_type, int, &fe_type_c, 0644);

MODULE_PARM_DESC(debug, "Debug level. Default: 0");
MODULE_PARM_DESC(fe_type, "Frontend type\n"
			  "\t\t\t0: DVB-S\n"
			  "\t\t\t1: DVB-C\n"
			  "\t\t\t2: DVB-T\n"
			  "\t\t\tDefault: 0: DVB-S");

struct dvb_dummy {
	struct platform_device *plat_dev;
	int instance;

#if 0
	struct dmx_frontend hw_frontend;
#endif
	struct dmx_frontend mem_frontend;
	struct dmxdev dmxdev;
	struct dvb_adapter dvb_adapter;
	struct dvb_demux demux;
#if 0
	struct dvb_frontend *fe;
	struct dvb_net dvbnet;
#endif

	int feeding;
	struct mutex feedlock; /* protects feeding variable */
};

static int dvb_dummy_start_feed(struct dvb_demux_feed *feed)
{
	struct dvb_demux *demux = feed->demux;
	struct dvb_dummy *dummy = (struct dvb_dummy *) demux->priv;

	if (dummy == NULL)
		return -EINVAL;

	if (debug)
		printk(KERN_INFO "dvb_dummy_adapter%d: "
		       "Start feed: pid = 0x%x index = %d\n",
		       dummy->instance, feed->pid, feed->index);

	if (!demux->dmx.frontend)
		return -EINVAL;

	mutex_lock(&dummy->feedlock);
	if (dummy->feeding++ == 0 && debug)
		printk(KERN_INFO
		       "dvb_dummy_adapter%d: Starting transport\n",
		       dummy->instance);
	mutex_unlock(&dummy->feedlock);
	return 0;
}

static int dvb_dummy_stop_feed(struct dvb_demux_feed *feed)
{
	struct dvb_demux *demux = feed->demux;
	struct dvb_dummy *dummy = (struct dvb_dummy *) demux->priv;

	if (dummy == NULL)
		return -EINVAL;

	if (debug)
		printk(KERN_INFO "dvb_dummy_adapter%d: "
		       "Stop feed: pid = 0x%x index = %d\n",
		       dummy->instance, feed->pid, feed->index);

	mutex_lock(&dummy->feedlock);
	if (--dummy->feeding == 0 && debug)
		printk(KERN_INFO
		       "dvb_dummy_adapter%d: Stopping transport\n",
		       dummy->instance);
	mutex_unlock(&dummy->feedlock);

	return 0;
}

static int dvb_dummy_register(struct dvb_dummy *dummy)
{
	struct dvb_adapter *dvb_adapter;
	struct dvb_demux *dvbdemux;
	struct dmx_demux *dmx;
	int ret;

	ret = dvb_register_adapter(&dummy->dvb_adapter, "dvb_dummy_adapter",
				   THIS_MODULE, &dummy->plat_dev->dev,
				   adapter_nr);
	if (ret < 0)
		goto err_out;

	dvb_adapter = &dummy->dvb_adapter;

	dvbdemux = &dummy->demux;

	dvbdemux->priv = (void *) dummy;

	dvbdemux->filternum = 256;
	dvbdemux->feednum = 256;
	dvbdemux->start_feed = dvb_dummy_start_feed;
	dvbdemux->stop_feed = dvb_dummy_stop_feed;
	dvbdemux->dmx.capabilities = (DMX_TS_FILTERING |
		DMX_SECTION_FILTERING | DMX_MEMORY_BASED_FILTERING);
	ret = dvb_dmx_init(dvbdemux);
	if (ret < 0)
		goto err_dvb_unregister_adapter;

	dmx = &dvbdemux->dmx;

#if 0
	dummy->hw_frontend.source = DMX_FRONTEND_0;
#endif
	dummy->mem_frontend.source = DMX_MEMORY_FE;
	dummy->dmxdev.filternum = 256;
	dummy->dmxdev.demux = dmx;

	ret = dvb_dmxdev_init(&dummy->dmxdev, dvb_adapter);
	if (ret < 0)
		goto err_dvb_dmx_release;

#if 0
	ret = dmx->add_frontend(dmx, &dummy->hw_frontend);
	if (ret < 0)
		goto err_dvb_dmxdev_release;

	ret = dmx->add_frontend(dmx, &dummy->mem_frontend);
	if (ret < 0)
		goto err_remove_hw_frontend;
	ret = dmx->add_frontend(dmx, &dummy->mem_frontend);
#else
	ret = dmx->add_frontend(dmx, &dummy->mem_frontend);
	if (ret < 0)
		goto err_dvb_dmxdev_release;
#endif

	ret = dmx->connect_frontend(dmx, &dummy->mem_frontend);
	if (ret < 0)
		goto err_remove_mem_frontend;

#if 0
	switch (fe_type[dummy->instance]) {
	case 1:
		dummy->fe = dvb_attach(dvb_dummy_fe_qam_attach);
		break;
	case 2:
		dummy->fe = dvb_attach(dvb_dummy_fe_ofdm_attach);
		break;
	default:
		dummy->fe = dvb_attach(dvb_dummy_fe_qpsk_attach);
		break;
	}
	ret = (dummy->fe == NULL) ? -1 : 0;
	if (ret < 0)
		goto err_disconnect_frontend;

	ret = dvb_register_frontend(dvb_adapter, dummy->fe);
	if (ret < 0)
		goto err_release_frontend;

	dvb_net_init(dvb_adapter, &dummy->dvbnet, dmx);
#endif

	printk(KERN_INFO "dvb_dummy_adapter%d: DVB Demux registered\n",
	       dummy->instance);
	printk(KERN_INFO "dvb_dummy_adapter%d: Registered DVB adapter%d\n",
	       dummy->instance, dummy->dvb_adapter.num);

	mutex_init(&dummy->feedlock);
	return ret;

#if 0
err_release_frontend:
	if (dummy->fe->ops.release)
		dummy->fe->ops.release(dummy->fe);
err_disconnect_frontend:
	dmx->disconnect_frontend(dmx);
#endif
err_remove_mem_frontend:
	dmx->remove_frontend(dmx, &dummy->mem_frontend);
#if 0
err_remove_hw_frontend:
	dmx->remove_frontend(dmx, &dummy->hw_frontend);
#endif
err_dvb_dmxdev_release:
	dvb_dmxdev_release(&dummy->dmxdev);
err_dvb_dmx_release:
	dvb_dmx_release(dvbdemux);
err_dvb_unregister_adapter:
	dvbdemux->priv = NULL;
	dvb_unregister_adapter(dvb_adapter);
err_out:
	return ret;
}

static void dvb_dummy_unregister(struct dvb_dummy *dummy)
{
	struct dvb_adapter *dvb_adapter;
	struct dvb_demux *dvbdemux;
	struct dmx_demux *dmx;

	printk(KERN_INFO "dvb_dummy_adapter%d: DVB Frontend unegister\n",
	       dummy->instance);
	printk(KERN_INFO "dvb_dummy_adapter%d: Unregister DVB adapter%d\n",
	       dummy->instance, dummy->dvb_adapter.num);

	dvb_adapter = &dummy->dvb_adapter;
	dvbdemux = &dummy->demux;
	dmx = &dvbdemux->dmx;

	dmx->close(dmx);
#if 0
	dvb_net_release(&dummy->dvbnet);
#endif
	dmx->remove_frontend(dmx, &dummy->mem_frontend);
#if 0
	dmx->remove_frontend(dmx, &dummy->hw_frontend);
#endif
	dvb_dmxdev_release(&dummy->dmxdev);
	dvb_dmx_release(dvbdemux);
	dvbdemux->priv = NULL;
#if 0
	dvb_unregister_frontend(dummy->fe);
	dvb_frontend_detach(dummy->fe);
#endif
	dvb_unregister_adapter(dvb_adapter);
}


static int dvb_dummy_probe(struct platform_device *plat_dev)
{
	int ret;
	struct dvb_dummy *dummy;

	dummy = kzalloc(sizeof(struct dvb_dummy), GFP_KERNEL);
	if (dummy == NULL) {
		printk(KERN_ERR
		       "dvb_dummy_adapter: out of memory for adapter %d\n",
		       plat_dev->id);
		return -ENOMEM;
	}

	dummy->plat_dev = plat_dev;
	dummy->instance = plat_dev->id;

	platform_set_drvdata(plat_dev, dummy);

	ret = dvb_dummy_register(dummy);
	if (ret < 0) {
		platform_set_drvdata(plat_dev, NULL);
		kfree(dummy);
	}
	return ret;
}

static int dvb_dummy_remove(struct platform_device *plat_dev)
{
	struct dvb_dummy *dummy;

	dummy = platform_get_drvdata(plat_dev);
	if (dummy == NULL)
		return 0;

	dvb_dummy_unregister(dummy);

	platform_set_drvdata(plat_dev, NULL);
	kfree(dummy);
	return 0;
}

static struct platform_device_id dvb_dummy_platform_id_table[] = {
	{ "dvb_dummy_adapter", 0 },
	{ },
};
MODULE_DEVICE_TABLE(platform, dvb_dummy_platform_id_table);

static struct platform_driver dvb_dummy_platform_driver = {
	.probe = dvb_dummy_probe,
	.remove = dvb_dummy_remove,
	.id_table = dvb_dummy_platform_id_table,
	.driver = {
		.name = "dvb_dummy_adapter",
	},
};

static int __init dvb_dummy_init(void)
{
	int ret = 0;
	int i, n;
	struct platform_device *plat_dev;

	printk(KERN_INFO
	       "dvb_dummy_adapter: Begin initialization, version %s\n",
	       DVB_DUMMY_VERSION);

	n = fe_type_c;
	if (n < 1 || n >= DVB_MAX_ADAPTERS) {
		printk(KERN_ERR "dvb_dummy_adapter: "
		       "Illegal number (%d) of frontend types specified\n", n);
		ret = -EINVAL;
		goto init_exit;
	}

	ret = platform_driver_register(&dvb_dummy_platform_driver);
	if (ret) {
		printk(KERN_ERR "dvb_dummy_adapter: "
		       "Error %d from platform_driver_register()\n", ret);
		goto init_exit;
	}

	for (i = 0; i < n; i++) {
		plat_dev = platform_device_register_simple("dvb_dummy_adapter",
							   i, NULL, 0);
		if (IS_ERR(plat_dev)) {
			printk(KERN_ERR "dvb_dummy_adapter: could not allocate"
			       "and register instance %d\n", i);
			ret = (i == 0) ? -ENODEV : 0;
			break;
		}
	}

init_exit:
	printk(KERN_INFO "dvb_dummy_adapter: End initialization\n");
	return ret;
}

static void __exit dvb_dummy_exit(void)
{
	printk(KERN_INFO "dvb_dummy_adapter: Begin exit\n");
	platform_driver_unregister(&dvb_dummy_platform_driver);
	printk(KERN_INFO "dvb_dummy_adapter: End exit\n");
}

module_init(dvb_dummy_init);
module_exit(dvb_dummy_exit);
