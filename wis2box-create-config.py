import os
import random
import string
import datetime


def get_bounding_box(country_code):
    """
    provide the initial bounding box for the wis2box
    using the country's 3-letter ISO code
    using the data from config-templates/bounding_box_lookup.json

    use bounding box for the whole world if no value is found in
    the config-templates/bounding_box_lookup.json file

    country_code: string. 3-letter ISO code for the country
    returns: tuple. (minx, miny, maxx, maxy)
    """

    bounding_box = [-180, -90, 180, 90]

    # try to import the json module
    # if it fails, print a message and use the whole world as bounding box
    # if it succeeds, get the bounding box for the country from the json file
    try:
        import json
    except ImportError:
        print("Please install the json module to get bounding box from presets") # noqa
    else:
        print(f"Getting bounding box for '{country_code}'.")
        # get the path to the data
        data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "config-templates",
            "bounding_box_lookup.json"
        )
        # open the file
        with open(data_path) as json_file:
            # load the data
            data = json.load(json_file)
            # get the bounding box for the country
            if country_code in data and "bounding_box" in data[country_code]:
                bbox = data[country_code]["bounding_box"]
                if "min_lat" not in bbox or "min_lon" not in bbox or "max_lat" not in bbox or "max_lon" not in bbox: # noqa 
                    print(f"Bounding box for '{country_code}' is invalid.")
                    print("Using the bounding box for the whole world.")
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
    while answer != "y" and answer != "exit":
        print("Please enter the bounding box for as a comma-separated list of four numbers:") # noqa
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


def get_country_and_center_id():
    """
    Asks the user for the 3-letter ISO country-code
    and a string identifying the center hosting the wis2box.

    returns: tuple. (country_code, center_id)
    """
    answer = ""
    while answer != "y":
        if answer == "exit":
            exit()
        print("Please enter your 3-letter ISO country-code:")
        country_code = input()
        # check that the input is a 3-letter string
        # if not repeat the question
        while len(country_code) != 3:
            print("The country-code must be a 3-letter string.")
            print("Please enter your 3-letter ISO country-code:")
            country_code = input()
        # make sure the country-code is lowercase
        country_code = country_code.lower()
        print("Please enter the centre-id for your wis2box:")
        center_id = str(input()).lower()
        # check that the input is valid
        # if not repeat the question
        while '#' in center_id or '+' in center_id or ' ' in center_id or len(center_id) < 8: # noqa
            print("The centre-id can not contain spaces, the '+' or '#' character and must be at least 8 characters long.") # noqa
            print("Please enter the string identifying the center hosting the wis2box:") # noqa
            center_id = str(input()).lower()
        # ask the user to confirm their choice and give them the option to change it # noqa
        # and give them the option to exit the script
        print("The country-code will be set to:")
        print(f"  {country_code}")
        print("The centre-id will be set to:")
        print(f"  {center_id}")
        print("Is this correct? (y/n/exit)")
        answer = input()
    return (country_code, center_id)


def get_password(password_name):
    """
    asks the user to enter a password or to use a randomly generated password
    returns: string. the password to be used for the password_name
    """
    password = None

    answer = ""
    while answer != "y" and answer != "n":
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


def get_wis2box_url():
    """
    asks the user to enter the URL of the wis2box

    returns: string. the URL of the wis2box
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
        while not wis2box_url.startswith("http://") and not wis2box_url.startswith("https://"): # noqa
            print("The URL must start with http:// or https://")
            print("Please enter the URL of the wis2box:")
            wis2box_url = input()
        # ask the user to confirm their choice and give them the option to change it # noqa
        print("The URL of the wis2box will be set to:")
        print(f"  {wis2box_url}")
        print("Is this correct? (y/n/exit)")
        answer = input()
    return wis2box_url


def create_dev_env(config_dir):
    """
    creates the dev.env file in the config_dir

    config_dir: string. path to the config directory
    """

    with open("dev.env", "w") as f:
        f.write(f"WIS2BOX_HOST_DATADIR={config_dir}\n")
        f.write("\n")
        wis2box_url = get_wis2box_url()
        f.write(f"WIS2BOX_URL={wis2box_url}\n")
        f.write(f"WIS2BOX_API_URL={wis2box_url}/oapi\n")
        f.write("\n")
        # use the default username wis2box for WIS2BOX_STORAGE_USERNAME
        f.write("WIS2BOX_STORAGE_USERNAME=wis2box\n")
        # get password for WIS2BOX_STORAGE_PASSWORD and write it to dev.env
        f.write(get_password("WIS2BOX_STORAGE_PASSWORD"))
        f.write("\n")
        # write default port and host for WIS2BOX_BROKER
        f.write("WIS2BOX_BROKER_PORT=1883\n")
        f.write("WIS2BOX_BROKER_HOST=mosquitto\n")
        # use the default username wis2box for WIS2BOX_BROKER_USERNAME
        f.write("WIS2BOX_BROKER_USERNAME=wis2box\n")
        # get password for WIS2BOX_BROKER_PASSWORD and write it to dev.env
        f.write(get_password("WIS2BOX_BROKER_PASSWORD"))
        f.write("\n")
        # update WIS2BOX_PUBLIC_BROKER settings after updating broker defaults
        f.write("# update WIS2BOX_PUBLIC_BROKER settings after updating broker defaults\n") # noqa
        f.write("WIS2BOX_BROKER_PUBLIC=mqtt://${WIS2BOX_BROKER_USERNAME}:${WIS2BOX_BROKER_PASSWORD}@mosquitto:1883\n") # noqa
        # update minio settings after updating storage and broker defaults
        f.write("\n")
        f.write("# update minio settings after updating storage and broker defaults\n") # noqa
        f.write("MINIO_ROOT_USER=${WIS2BOX_STORAGE_USERNAME}\n")
        f.write("MINIO_ROOT_PASSWORD=${WIS2BOX_STORAGE_PASSWORD}\n")
        f.write("MINIO_NOTIFY_MQTT_USERNAME_WIS2BOX=${WIS2BOX_BROKER_USERNAME}\n") # noqa
        f.write("MINIO_NOTIFY_MQTT_PASSWORD_WIS2BOX=${WIS2BOX_BROKER_PASSWORD}\n") # noqa
        f.write("MINIO_NOTIFY_MQTT_BROKER_WIS2BOX=tcp://${WIS2BOX_BROKER_HOST}:${WIS2BOX_BROKER_PORT}\n") # noqa
    print("*"*80)
    print("The file dev.env has been created in the current directory.")
    print("*"*80)


def create_config_dir():
    """
    creates the directory config_dir
    if the directory already exists, asks the user if they want to overwrite the existing files # noqa

    returns: string. the path to the directory where the configuration files are to be stored # noqa
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

    # check if the directory exists
    if os.path.isdir(config_dir):
        # if it exists warn the user
        # tell them that the directory needs to be remove to continue
        print("WARNING:")
        print(f"The directory {config_dir} already exists.")
        print("Please remove the directory to restart the configuration process.") # noqa
        exit()
    else:
        # if it does not exist, create it
        os.system("mkdir " + config_dir)
        # check if the directory was created
        if not os.path.isdir(config_dir):
            print("ERROR:")
            print(f"The directory {config_dir} could not be created.")
            print("Please check the path and your permissions.")
            exit()
    print(f"The directory {config_dir} has been created.")
    return config_dir


def create_datamappings_file(config_dir, country_code, center_id):
    """
    creates the data-mappings file in the directory config_dir

    config_dir: string. the path to the directory where the configuration files are to be stored # noqa
    country_code: string. the country code of the wis2box
    center_id: string. the center id of the wis2box
    """

    new_config_file = config_dir + "/data-mappings.yml"

    with open("config-templates/data-mappings-template.yml", "r") as f:
        config_file = f.read()
        config_file = config_file.replace("COUNTRY_CODE", country_code)
        config_file = config_file.replace("CENTRE_ID", center_id)
        with open(new_config_file, "w") as f:
            f.write(config_file)

    # also add mappings.json from config-templates to config_dir
    with open("config-templates/csv2bufr_mappings.json", "r") as f:
        mappings_file = f.read()
        with open(config_dir + "/csv2bufr_mappings.json", "w") as f:
            f.write(mappings_file)

    print("*"*80)
    print("Initial data_mappings.yml and csv2bufr_mappings.json have been created") # noqa
    print("Please review the files and update them as needed.") # noqa
    print("*"*80)


def create_metadata_file(config_dir, country_code, center_id, center_name, wis2box_email, bounding_box, template): # noqa
    """
    creates the metadata file in the directory config_dir

    config_dir: string. the path to the directory where the configuration files are to be stored # noqa
    country_code: string. the country code of the wis2box
    center_id: string. the center id of the wis2box
    template: string. synop or temp
    
    returns: string. the path to the metadata file
    """

    # get current date as a string
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # create directory for discovery metadata if it does not exist
    if not os.path.exists(config_dir + "/metadata/discovery"):
        os.makedirs(config_dir + "/metadata/discovery")

    new_config_file = f"{config_dir}/metadata/discovery/metadata-{template}.yml" # noqa
    with open(f"config-templates/metadata-{template}-template.yml", "r") as f: # noqa
        config_file = f.read()
        # replace PUBLICATION_DATE with current date
        config_file = config_file.replace("PUBLICATION_DATE", current_date)
        # replace START_DATE with current date
        config_file = config_file.replace("START_DATE", current_date)
        # replace CREATION_DATE with current date
        config_file = config_file.replace("CREATION_DATE", current_date)
        # replace COUNTRY_CODE, CENTRE_ID, CENTRE_NAME
        config_file = config_file.replace("COUNTRY_CODE", country_code)
        config_file = config_file.replace("CENTRE_ID", center_id)
        config_file = config_file.replace("CENTRE_NAME", center_name)
        # replace email address
        config_file = config_file.replace("WIS2BOX_EMAIL", wis2box_email)
        # replace bounding box
        config_file = config_file.replace("MINX, MINY, MAXX, MAXY", str(bounding_box)) # noqa
        with open(new_config_file, "w") as f:
            f.write(config_file)
            print("Created new metadata-file:")
            print(f"    {new_config_file}")
    return new_config_file


def create_metadata_files(config_dir, country_code, center_id):
    """
    creates the metadata files in the directory config_dir

    config_dir: string. the path to the directory where the configuration files are to be stored # noqa
    country_code: string. the country code of the country hosting the wis2box
    center_id: string. the center id of the organization hosting the wis2box
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

    # ask for the name of the center
    answer = ""
    while answer != "y":
        if answer == "exit":
            exit()
        print("Please enter the name of your organization:")
        center_name = input()
        print("Your organization name will be set to:")
        print(f"    {center_name}")
        print("Is this correct? (y/n/exit)")
        answer = input()

    # get an initial bounding box for the country
    bounding_box = get_bounding_box(country_code)

    create_metadata_file(
        config_dir,
        country_code,
        center_id,
        center_name,
        wis2box_email,
        bounding_box,
        template="synop"
    )
    create_metadata_file(
        config_dir,
        country_code,
        center_id,
        center_name,
        wis2box_email,
        bounding_box,
        template="temp"
    )

    print("*"*80)
    print(f"Initial metadata files have been created in the directory {config_dir}.") # noqa
    print("Please review the files and edit where necessary.")
    print("*"*80)


def create_station_list(config_dir):
    """
    creates the station list file in the directory config_dir

    config_dir: string. the path to the directory where the configuration files are to be stored # noqa
    """

    # create directory for station metadata if it does not exist
    if not os.path.exists(config_dir + "/metadata/station"):
        os.makedirs(config_dir + "/metadata/station")

    # create station list file
    new_config_file = f"{config_dir}/metadata/station/station_list.csv"
    with open("config-templates/station_list_example.csv", "r") as f:
        config_file = f.read()
        with open(new_config_file, "w") as f:
            f.write(config_file)

    print("*"*80)
    print(f"Created the file {new_config_file}.")
    print("Please add your stations to this file.")
    print("*"*80)


def get_config_dir():
    """
    reads the value of WIS2BOX_HOST_DATADIR from dev.env

    returns: string. the path to the directory where the configuration files are to be stored # noqa
    """

    config_dir = None
    with open("dev.env", "r") as f:
        lines = f.readlines()
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
    main function

    creates the configuration files for the wis2box
    """

    config_dir = None

    # check if dev.env exists
    # if it does, read the value for WIS2BOX_HOST_DATADIR
    # or give the user the option to recreate dev.env
    if os.path.isfile("dev.env"):
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
    if not os.path.isfile("dev.env"):
        create_dev_env(config_dir)

    country_code, center_id = get_country_and_center_id()

    print("*"*80)
    print("Creating initial configuration for surface and upper-air data.")
    print("*"*80)

    create_metadata_files(config_dir, country_code, center_id)
    create_datamappings_file(config_dir, country_code, center_id)
    create_station_list(config_dir)

    print("The configuration is complete.")
    exit()


if __name__ == "__main__":
    main()
