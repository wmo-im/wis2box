.. _gts-headers-in-wis2:

Optional: adding GTS headers to WIS2 notifications during the transition period
===============================================================================

Overview
--------

This section provides guidance how to add GTS headers to your WIS2 notifications.

By adding GTS headers to your WIS2 notifications, you can stop your MSS and still have your data available on the GTS during the transition period.

To enable the WIS2 to GTS Gateway to correctly identify the data to be republished on the GTS, you need to include the GTS property in the WIS2 Notification Message as follows:

```json
{
  "properties": {
    "gts": {
      "ttaaii": "FTAE31",
      "cccc": "VTBB"
    }
  }
}
```

The wis2box can add these to your WIS2 Notifications automatically, provided you specify the additional file `gts_headers_mappings.json` that contains the required information to map the GTS headers to the incoming filenames.

Note that this is optional and only required if you want to turn off the system responsible for sending data to the GTS during the transition period.

gts_headers_mappings.json
-------------------------

If you want to add GTS headers to your WIS2 notifications, you need to create a JSON file that maps the GTS headers to the incoming filenames. 

The JSON file should be named `gts_headers_mappings.json` and should be placed in the directory you defined using the `WIS2BOX_HOST_DATADIR` environment variable.

The CSV should contain three columns: `string_in_filepath`, `TTAAii`, and `CCCC`.

Example content for `gts_headers_mappings.json`:

```
string_in_filepath,TTAAii,CCCC
ISMD01LIIB,ISMD01,LIBB
ISMD02LIIB,ISMD02,LIBB
```

In this example, whenever `ISMD01LIIB` or `ISMD02LIIB` is contained in the file-path of the incoming file,
the corresponding GTS-headers will be added to the WIS2 Notification Message as a dictionary in the `properties` field:

```json
{
  "properties": {
    "gts": {
      "ttaaii": "ISMD01",
      "cccc": "LIBB"
    }
  }
}
```

If the `gts_headers_mappings.json` file is not present in the directory you defined using the `WIS2BOX_HOST_DATADIR` environment variable, the wis2box will not add any GTS headers to the WIS2 Notification Message.


