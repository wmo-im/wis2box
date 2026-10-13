.. _export-import-for-backup:

Configuration backup operations
===============================

Basic functionality for exporting and importing wis2box configuration data is available from the command line within the wis2box-management.

These functions can be used to quickly configure a 2nd wis2box instance with the same datasets and stations as the original instance.

Exporting configuration
-----------------------

To export the current configuration of a wis2box instance, use the following command:

```
python3 wis2box-ctl.py execute wis2box metadata export
```

The output will look something like this:
```
Exported 3 discovery-metadata items
Exported 61 stations items
Wrote metadata export to /data/wis2box/export/metadata-export.json
Available on docker-host at /home/wis2box-test/wis2box-data/export/metadata-export.json
```

Note that the first path indicates the location within the container, while the second path shows the location on the wis2box-host.

You can use commands like `scp` to copy the exported configuration file from the current host to the machine hosting the wis2box instance where you want to import the configuration.

Importing configuration
-----------------------

Make sure to place the exported configuration file in the directory defined by `WIS2BOX_HOST_DATADIR` on the host of the new wis2box-instance.

Any file placed in the directory defined by `WIS2BOX_HOST_DATADIR` will be available in the directory `/data/wis2box/` within the wis2box-management container.

Once you have copied the file, you can import the configuration into the new wis2box instance using the following command:

```
python3 wis2box-ctl.py execute wis2box metadata import /data/wis2box/metadata-export.json
```

After running the import command, the new wis2box instance will be configured with the same datasets and stations as the original instance.