wis2box environment create
wis2box environment show
wis2box data setup --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed
wis2box api add-collection --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed $WIS2BOX_DATADIR/metadata/discovery/surface-weather-observations.yml
wis2box metadata station cache $WIS2BOX_DATADIR/metadata/station/station_list.csv
wis2box metadata station publish-collection
wis2box metadata discovery publish $WIS2BOX_DATADIR/metadata/discovery/surface-weather-observations.yml
wis2box data ingest --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed --path $WIS2BOX_DATADIR/observations/WIGOS_0-454-2-AWSNAMITAMBO_2021-07-07.csv
wis2box api add-collection-items --recursive --path $WIS2BOX_DATADIR/data/public
