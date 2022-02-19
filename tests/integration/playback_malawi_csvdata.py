#!/usr/bin/env python3

import logging
import os
from pathlib import Path
import time

# time between data collections... in seconds.
#
# download sample Malawi data from here: https://wmo-teams.atlassian.net/wiki/spaces/WIS2/pages/302907405/WIS+2.0+in+a+box
# unzip it, and point input_directory to it:
input_directory="Malawi synop data"

# default place in a wis2box container.
output_directory='/data/wis2box/data/incoming'

logger = logging.getLogger(__name__)
logger.setLevel( logging.INFO )

os.chdir(input_directory)

filenames = os.listdir()

filehandles={}

for fn in filenames:
    filehandles[fn] = open(fn,'r')

print(filehandles)

obsread=1
while obsread > 0:
    obsread = 0 
    for fn in filenames:
        try:
            csv_ob = filehandles[fn].readline()
        except Exception as ex:
            logger.info( f'failed to read {fn}: {ex}' )
            logger.debug('Exception details: ', exc_info=True)
            continue
        if csv_ob:
             obsread += 1
        print(csv_ob)
        sitename=fn.replace('_SYNOP.csv','')

        fields=csv_ob.split(',')
        if 'TIMESTAMP' in fields[0]:
            logger.info(f'skipping header in {fn}:{csv_ob}')
            continue
 
        print(f'fields[0] {fields[0]}' )
        # real obs start with a datetime.
        if fields[0][0:4] != '"202':
            logger.warning(f'no datetime for {sitename}: line: {csv_ob}')
            continue

        datetime=fields[0].replace('"','').replace(' ','T').replace(':','')

        output_path = Path( output_directory ) / f'WIGOS_0-454-2-{sitename}_{datetime}.csv' 
        print(f'outname: {output_path}' )
        with open(output_path,'w') as of:
            of.write(csv_ob)
   
    time.sleep(replay_observation_interval)
     


for fn in filenames:
    filehandles[fn].close()
