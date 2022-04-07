.. _auth:

Authentication and Access control
=================================

wis2box provides built in access control for the WAF and API on a topic hierarchy basis. Configuration is done
using the wis2box command line utility. Authentication tokens are only required for topics that have access control
configured.

Adding Access Control
---------------------

All topic hierarchies in wis2box are open by default. A topic becomes closed, with access control applied, the
first time a token is generated for a topic hierarchy.

.. note::

    Make sure you are logged into the wis2box container when using the wis2box CLI

.. code-block:: bash

    wis2box auth add-token --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed mytoken


If no token is provided, a random string will be generated. Be sure to the record token now, there is no
way to retrieve it once it is lost.

Authenticating
--------------

Once a token has been generated for a topic, it can be used by appending as an argument. It can also be
passed as an Authentication header with a bearer token. Token credentials can also be validated using the
wis2box command line utility.

.. code-block:: bash

    wis2box auth show
    wis2box auth has_access --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed mytoken
    wis2box auth has_access --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed notmytoken


Removing Access Control
-----------------------

A topic becomes open and no longer requires authentication when all tokens have been deleted. This can be done by
deleting individual tokens, or all tokens for a given topic hierarchy.

.. code-block:: bash

    wis2box auth remove-tokens --topic-hierarchy data.core.observations-surface-land.mw.FWCL.landFixed
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
