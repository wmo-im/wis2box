###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import datetime
import json
import os
from pathlib import Path
import random
import string
from string import Template
from typing import Tuple


def get_bounding_box(country_code: str) -> Tuple[str, str, str, str]:
    """
    provide the initial bounding box for the wis2box
    using the country's 3-letter ISO code
    using the data from config-templates/bounding_box_lookup.json

    use bounding box for the whole world if no value is found in
    the config-templates/bounding_box_lookup.json file

    :param country_code: `str` 3-letter ISO code for the country

    :returns: `tuple` of (minx, miny, maxx, maxy)
    """

    bounding_box = [-180, -90, 180, 90]

    print(f"Getting bounding box for '{country_code}'.")

    # get the path to the data
    data_path = Path(__file__).parent / 'config-templates' / 'bounding_box_lookup.json'  # noqa

    # open the file
    with data_path.open() as fh:
        # load the data
        data = json.load(fh)
        # get the bounding box for the country
        if country_code in data and "bounding_box" in data[country_code]:
            bbox = data[country_code]["bounding_box"]
            if not {'min_lat', 'min_lon', 'max_lat', 'max_lon'} <= bbox.keys():
                print(f"Bounding box for '{country_code}' is invalid.")
                print("Using global bounding box.")
            else:
                MIN_LAT = bbox["min_lat"]
                MIN_LON = bbox["min_lon"]
                MAX_LAT = bbox["max_lat"]
                MAX_LON = bbox["max_lon"]
                # create bounding box as comma-separated list of four numbers # noqa
                bounding_box = f"{MIN_LON},{MIN_LAT},{MAX_LON},{MAX_LAT}"
        else:
            print(f"No bounding box found for '{country_code}'.")
            print("Using the bounding box for the whole world.")

    # ask the user to accept the bounding box or to enter a new one
    print(f"bounding box: {bounding_box}.")
    print("Do you want to use this bounding box? (y/n/exit)")
    answer = input()

    while answer not in ['y', 'exit']:
        print("Please enter the bounding box as a comma-separated list of four numbers:") # noqa
        print("The first two numbers are the coordinates of the lower left corner of the bounding box.") # noqa
        print("The last two numbers are the coordinates of the upper right corner of the bounding box.") # noqa
        print("For example: 5.5,47.2,15.5,55.2")
        bounding_box = input()
        print(f"bounding box: {bounding_box}.")
        print("Do you want to use this bounding box? (y/n/exit)")
        answer = input()

    if answer == "exit":
        exit()

    return bounding_box


def get_country_and_centre_id() -> Tuple[str, str]:
    """
    Asks the user for the 3-letter ISO country-code
    and a string identifying the centre hosting the wis2box.

    :returns: `tuple` of (country_code, centre_id)
    """

    answer = ""

    while answer != "y":
        if answer == "exit":
            exit()

        print("Please enter your 3-letter ISO country code:")
        country_code = input()

        # check that the input is a 3-letter string
        # if not repeat the question
        while len(country_code) != 3:
            print("The country code must be a 3-letter string.")
            print("Please enter your 3-letter ISO country code:")
            country_code = input()

        # make sure the country code is lowercase
        country_code = country_code.lower()

        print("Please enter the centre-id for your wis2box:")
        centre_id = str(input()).lower()

        # check that the input is valid
        # if not repeat the question
        while any([x in centre_id for x in ['#', '+', ' ']]) or len(centre_id) < 3:  # noqa
            print("The centre-id cannot contain spaces or the '+' or '#' characters, and must be at least 3 characters long.") # noqa
            print("Please enter the string identifying the centre hosting the wis2box:") # noqa
            centre_id = str(input()).lower()

        # ask the user to confirm their choice and give them the option to change it # noqa
        # and give them the option to exit the script
        print("The country-code will be set to:")
        print(f"  {country_code}")
        print("The centre-id will be set to:")
        print(f"  {centre_id}")
        print("Is this correct? (y/n/exit)")
        answer = input()

    return (country_code, centre_id)


def get_password(password_name: str) -> str:
    """
    asks the user to enter a password or to use a randomly generated password

    :param password_name: `str` of password entered

    :returns: `str` of password to be used
    """

    password = None

    answer = ""
    while answer not in ['y', 'n']:
        if answer == "exit":
            exit()

        print(f"Do you want to use a randomly generated password for {password_name} (y/n/exit)") # noqa
        answer = input()

    if answer == "y":
        password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8)) # noqa
        print(f"{password_name}={password}")

    while answer != "y":
        if answer == "exit":
            exit()

        print("Please enter the password to be used for the WIS2BOX_STORAGE_PASSWORD:") # noqa
        password = input()

        # check if the password is at least 8 characters long
        # if not repeat the question
        while len(password) < 8:
            print("The password must be at least 8 characters long.")
            print(f"Please enter the password to be used for the {password_name}:") # noqa
            password = input()

        print(f"{password_name}={password}")
        print("Is this correct? (y/n/exit)")
        answer = input()

    return f"{password_name}={password}\n"


def get_wis2box_url() -> str:
    """
    asks the user to enter the URL of the wis2box

    :returns: `str` of wis2box URL
    """

    wis2box_url = None
    answer = ""

    while answer != "y":
        if answer == "exit":
            exit()

        # ask for the WIS2BOX_URL, use http://localhost as the default
        print("Please enter the URL of the wis2box:")
        print(" When running the wis2box locally, the default is http://localhost") # noqa
        print(" To enable remote access, please enter the public IP address or domain name of the server hosting the wis2box.") # noqa

        # check if the URL starts with http:// or https://
        # if not, ask the user to enter the URL again
        wis2box_url = ""
        wis2box_url = input()

        while not wis2box_url.startswith(("http://", "https://")):
            print("The URL must start with http:// or https://")
            print("Please enter the URL of the wis2box:")
            wis2box_url = input()

        # ask the user to confirm their choice and give them the option to change it # noqa
        print("The URL of the wis2box will be set to:")
        print(f"  {wis2box_url}")
        print("Is this correct? (y/n/exit)")
        answer = input()

    return wis2box_url


def create_dev_env(config_dir: str) -> None:
    """
    creates the dev.env file in the config_dir

    :param config_dir: `str` of path to the config directory

    :returns: None
    """

    dev_env = Path("dev.env")

    with dev_env.open("w") as fh:
        fh.write(f"WIS2BOX_HOST_DATADIR={config_dir}\n")
        fh.write("\n")
        wis2box_url = get_wis2box_url()
        fh.write(f"WIS2BOX_URL={wis2box_url}\n")
        fh.write(f"WIS2BOX_API_URL={wis2box_url}/oapi\n")
        fh.write("\n")
        # use the default username wis2box for WIS2BOX_STORAGE_USERNAME
        fh.write("WIS2BOX_STORAGE_USERNAME=wis2box\n")
        # get password for WIS2BOX_STORAGE_PASSWORD and write it to dev.env
        fh.write(get_password("WIS2BOX_STORAGE_PASSWORD"))
        fh.write("\n")
        # write default port and host for WIS2BOX_BROKER
        fh.write("WIS2BOX_BROKER_PORT=1883\n")
        fh.write("WIS2BOX_BROKER_HOST=mosquitto\n")
        # use the default username wis2box for WIS2BOX_BROKER_USERNAME
        fh.write("WIS2BOX_BROKER_USERNAME=wis2box\n")
        # get password for WIS2BOX_BROKER_PASSWORD and write it to dev.env
        fh.write(get_password("WIS2BOX_BROKER_PASSWORD"))
        fh.write("\n")
        # update WIS2BOX_PUBLIC_BROKER settings after updating broker defaults
        fh.write("# update WIS2BOX_PUBLIC_BROKER settings after updating broker defaults\n") # noqa
        fh.write("WIS2BOX_BROKER_PUBLIC=mqtt://${WIS2BOX_BROKER_USERNAME}:${WIS2BOX_BROKER_PASSWORD}@mosquitto:1883\n") # noqa
        # update minio settings after updating storage and broker defaults
        fh.write("\n")
        fh.write("# update minio settings after updating storage and broker defaults\n") # noqa
        fh.write("MINIO_ROOT_USER=${WIS2BOX_STORAGE_USERNAME}\n")
        fh.write("MINIO_ROOT_PASSWORD=${WIS2BOX_STORAGE_PASSWORD}\n")
        fh.write("MINIO_NOTIFY_MQTT_USERNAME_WIS2BOX=${WIS2BOX_BROKER_USERNAME}\n") # noqa
        fh.write("MINIO_NOTIFY_MQTT_PASSWORD_WIS2BOX=${WIS2BOX_BROKER_PASSWORD}\n") # noqa
        fh.write("MINIO_NOTIFY_MQTT_BROKER_WIS2BOX=tcp://${WIS2BOX_BROKER_HOST}:${WIS2BOX_BROKER_PORT}\n") # noqa

    print("*" * 80)
    print("The file dev.env has been created in the current directory.")
    print("*" * 80)


def create_config_dir() -> str:
    """
    Creates the directory config_dir

    If the directory already exists, asks the user if they want to overwrite
    the existing files

    :returns: `str` of path to directory where configuration files
              are to be stored
    """

    config_dir = ""
    answer = "n"

    while answer != "y":
        if answer == "exit":
            exit()

        print("Please enter the directory on the host where wis2box-configuration-files are to be stored:") # noqa
        config_dir = input()

        if config_dir == "":
            print("The directory cannot be empty.")
            continue

        print("Configuration-files will be stored in the following directory:") # noqa
        print(f"    {config_dir}")
        print("Is this correct? (y/n/exit)")
        answer = input()

    config_dir = Path(config_dir)

    # check if the directory exists
    if config_dir.is_dir():
        # if it exists warn the user
        # tell them that the directory needs to be remove to continue
        print("WARNING:")
        print(f"The directory {config_dir} already exists.")
        print("Please remove the directory to restart the configuration process.") # noqa
        exit()
    else:
        # if it does not exist, create it
        config_dir.mkdir()
        # check if the directory was created
        if not config_dir.is_dir():
            print("ERROR:")
            print(f"The directory {config_dir} could not be created.")
            print("Please check the path and your permissions.")
            exit()
    print(f"The directory {config_dir} has been created.")

    return config_dir


def create_datamappings_file(config_dir: str, country_code: str,
                             centre_id: str) -> None:
    """
    creates the data mappings file in the directory config_dir

    :param config_dir: `str` of path to directory where configuration files
                       are to be stored
    :param country_code: `str` of the country code of the wis2box
    :param centre_id: `str` of the centre id of the wis2box

    :returns: None
    """

    template_file = Path("config-templates/data-mappings.yml.tmpl")
    new_config_file = Path(config_dir) / "data-mappings.yml"
    csv2bufr_mappings_template_file = Path("config-templates/csv2bufr_mappings.json")  # noqa
    csv2bufr_mappings_file = Path(config_dir) / 'csv2bufr_mappings.json'

    template_vars = {
        'COUNTRY_CODE': country_code,
        'CENTRE_ID': centre_id
    }
    with template_file.open() as fh:
        config_file = Template(fh.read())
        result = config_file.substitute(template_vars)
        with new_config_file.open("w") as fh2:
            fh2.write(result)

    # also add mappings.json from config-templates to config_dir
    with csv2bufr_mappings_template_file.open() as fh:
        mappings_file = fh.read()
        with csv2bufr_mappings_file.open("w") as fh2:
            fh2.write(mappings_file)

    print("*" * 80)
    print("Initial data_mappings.yml and csv2bufr_mappings.json have been created") # noqa
    print("Please review the files and update as needed.")
    print("*" * 80)


def create_metadata_file(config_dir: str, country_code: str, centre_id: str,
                         centre_name: str, wis2box_email: str,
                         bounding_box: str, template: str) -> str:
    """
    creates the metadata file in the directory config_dir

    :param config_dir: `str` of the path to the directory where the configuration files are to be stored # noqa
    :param country_code: `str` of the country code of the wis2box
    :param centre_id: `str` of the centre id of the wis2box
    :param centre_name: `str` of centre name of the wis2box
    :param wis2box_email: `str` of centre email
    :param bounding_box: `str` of CSV of bounding box
    :param template: `str` of synop or temp
    
    :returns: `str` of the path to the metadata file
    """

    # get current date as a string
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    config_dir = Path(config_dir)
    discovery_metadata_dir = config_dir / 'metadata' / 'discovery'

    # create directory for discovery metadata if it does not exist
    if not discovery_metadata_dir.exists():
        discovery_metadata_dir.mkdir(parents=True)

    new_config_file = discovery_metadata_dir / f'metadata-{template}.yml'
    template_file = Path('config-templates') / f'metadata-{template}.yml.tmpl'  # noqa

    template_vars = {
        'PUBLICATION_DATE': current_date,
        'START_DATE': current_date,
        'CREATION_DATE': current_date,
        'COUNTRY_CODE': country_code,
        'CENTRE_ID': centre_id,
        'CENTRE_NAME': centre_name,
        'WIS2BOX_EMAIL': wis2box_email,
        'BOUNDING_BOX': bounding_box
    }

    with template_file.open() as fh:
        config_file = Template(fh.read())
        result = config_file.substitute(template_vars)
        with new_config_file.open("w") as fh2:
            fh2.write(result)
            print(f"Created new metadata file: {new_config_file}")

    return new_config_file.name


def create_metadata_files(config_dir: str, country_code: str,
                          centre_id: str) -> None:
    """
    creates the metadata files in the directory config_dir

    :config_dir: `str` of path to directory where configuration files
                 are to be stored # noqa
    :country_code: `str` of country code of the country hosting the wis2box
    :centre_id: `str` of centre id of the organization hosting the wis2box

    :returns: None
    """

    # ask for the email address of the wis2box administrator
    answer = ""
    wis2box_email = ""

    while answer != "y":
        if answer == "exit":
            exit()

        print("Please enter the email address of the wis2box administrator:")
        wis2box_email = input()
        print("The email address of the wis2box administrator will be set to:") # noqa
        print(f"    {wis2box_email}")
        print("Is this correct? (y/n/exit)")
        answer = input()

    # ask for the name of the centre
    answer = ""

    while answer != "y":
        if answer == "exit":
            exit()
        print("Please enter the name of your organization:")
        centre_name = input()
        print("Your organization name will be set to:")
        print(f"    {centre_name}")
        print("Is this correct? (y/n/exit)")
        answer = input()

    # get an initial bounding box for the country
    bounding_box = get_bounding_box(country_code)

    create_metadata_file(
        config_dir,
        country_code,
        centre_id,
        centre_name,
        wis2box_email,
        bounding_box,
        template="synop"
    )
    create_metadata_file(
        config_dir,
        country_code,
        centre_id,
        centre_name,
        wis2box_email,
        bounding_box,
        template="temp"
    )

    print("*" * 80)
    print(f"Initial metadata files created in directory {config_dir}.") # noqa
    print("Please review the files and edit where necessary.")
    print("*" * 80)


def create_station_list(config_dir: str) -> None:
    """
    creates the station list file in the directory config_dir

    :param config_dir: `str` of path to directory where configuration files
                       are to be stored

    :returns: None
    """

    station_metadata_dir = Path(config_dir) / 'metadata' / 'station'
    station_list_template_file = Path('config-templates') / 'station_list_example.csv'  # noqa

    # create directory for station metadata if it does not exist
    if not station_metadata_dir.exists():
        station_metadata_dir.mkdir()

    # create station list file
    new_config_file = station_metadata_dir / "station_list.csv"

    with station_list_template_file.open() as fh:
        config_file = fh.read()
        with new_config_file.open("w") as fh2:
            fh2.write(config_file)

    print("*" * 80)
    print(f"Created the file {new_config_file}.")
    print("Please add your stations to this file.")
    print("*" * 80)


def get_config_dir() -> str:
    """
    reads the value of WIS2BOX_HOST_DATADIR from dev.env

    returns: `str` of path to directory where configuration files
             are to be stored
    """

    config_dir = None

    with Path("dev.env").open() as fh:
        lines = fh.readlines()

        for line in lines:
            if "WIS2BOX_HOST_DATADIR" in line:
                config_dir = line.split("=")[1].strip()

        if not config_dir:
            print("WARNING:")
            print("The file dev.env does not contain the variable WIS2BOX_HOST_DATADIR.") # noqa
            print("Please edit the file and add the variable WIS2BOX_HOST_DATADIR.") # noqa
            print("Or remove dev.env and run 'python3 wis2box-create-config.py' again.") # noqa
            exit()

    return config_dir


def main():
    """
    mainline function

    creates the configuration files for the wis2box
    """

    config_dir = None
    dev_env = Path("dev.env")

    # check if dev.env exists
    # if it does, read the value for WIS2BOX_HOST_DATADIR
    # or give the user the option to recreate dev.env
    if dev_env.is_file():
        print("The file dev.env already exists in the current directory.")
        print("Do you want to recreate dev.env? (y/n/exit)")
        answer = input()

        if answer == "y":
            os.remove("dev.env")
        elif answer == "exit":
            exit()
        else:
            config_dir = get_config_dir()

    # if config_dir is not defined
    if not config_dir:
        config_dir = create_config_dir()

    # if dev.env does not exist
    # create it and write config_dir as the value for WIS2BOX_HOST_DATADIR to dev.env # noqa
    if not dev_env.is_file():
        create_dev_env(config_dir)

    country_code, centre_id = get_country_and_centre_id()

    print("*" * 80)
    print("Creating initial configuration for surface and upper-air data.")
    print("*" * 80)

    create_metadata_files(config_dir, country_code, centre_id)
    create_datamappings_file(config_dir, country_code, centre_id)
    create_station_list(config_dir)

    print("The configuration is complete.")
    exit()


if __name__ == "__main__":
    main()
