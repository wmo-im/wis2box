.. _auth:

Authentication and access control
=================================

wis2box provides built in access control for the WAF and API on a topic hierarchy basis. Configuration is done
using the wis2box command line utility. Authentication tokens are only required for topics that have access control
configured.

In addition, wis2box restricts access to the execution of wis2box processes and PUT/POST/DELETE requests to the stations collection.

Access control on paths
-----------------------

To add a token to the execution of a wis2box process, use the following command:

.. code-block:: bash

    wis2box auth add-token --path processes/wis2box

This will generate a random token that can be used to execute ``wis2box-synop2bufr`` and ``wis2box-csv2bufr``.

.. note::

   Be sure to record the token now, there is no way to retrieve it once it is lost.

To add a token to PUT/POST/DELETE requests to the stations collection, use the following command:

.. code-block:: bash

    wis2box auth add-token --path collections/stations

This will generate a random token that can be use to update the stations collection.

Adding Access Control on datasets
---------------------------------

All dataset in wis2box are open by default. A dataset becomes closed, with access control applied, the
first time a token is generated for a dataset

.. note::

    Make sure you are logged into the wis2box-management container when using the wis2box CLI

.. code-block:: bash

    wis2box auth add-token --metadata-id urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations mytoken


If no token is provided, a random string will be generated. Be sure to the record token now, there is no
way to retrieve it once it is lost.

Authenticating
--------------

Token credentials can be validated using the wis2box command line utility.

.. code-block:: bash

    wis2box auth show
    wis2box auth has-access-topic --metadata-id urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations mytoken
    wis2box auth has-access-topic --metadata-id urn:wmo:md:mw-mw_met_centre-test:surface-weather-observations notmytoken


Once a token has been generated, access to any data of that topic in the WAF or API requires token authentication.
Tokens are passed as a bearer token in the Authentication header or as an argument appended to the URI. Headers can be
easily added to requests using `cURL`_.

.. code-block:: bash

    curl -H "Authorization: Bearer mytoken" "http://localhost/oapi/collections/mw-mw_met_centre-test.data.core.weather.surface-based-observations.synop"
    curl -H "Authorization: Bearer notmytoken" "http://localhost/oapi/collections/mw-mw_met_centre-test.data.core.weather.surface-based-observations.synop"


Removing Access Control
-----------------------

A topic becomes open and no longer requires authentication when all tokens have been deleted. This can be done by
deleting individual tokens, or all tokens for a given topic hierarchy.

.. code-block:: bash

    wis2box auth remove-tokens --topic-hierarchy mw-mw_met_centre-test.data.core.weather.surface-based-observations.synop
    wis2box auth show


Extending Access Control
------------------------

wis2box provides access control out of the box with subrequests to wis2box-auth. wis2box-auth
could be replaced in nginx for another auth server like `Gluu`_ or a Web SSO like `LemonLDAP`_
or `Keycloak`_. These services are not yet configurable via the wis2box command line utility.

wis2box is intentionally plug and playable. Beyond custom authentication servers, extending wis2box
provides an overview of more modifications that can be made to wis2box.

.. _`Gluu`: https://gluu.org/
.. _`Keycloak`: https://www.keycloak.org/
.. _`LemonLDAP`: https://lemonldap-ng.org/
.. _`cURL`: https://curl.se/
