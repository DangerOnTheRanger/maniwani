Administering a Maniwani instance
=================================

This document is meant to be a reference on how to administer a Maniwani instance;
if you want a guide on how to deploy Maniwani, see `deploying.md` for more on that.
This is also not a reference on how to moderate a Maniwani deployment, either; for
that, look at `moderate.md`.


Changing a board's properties
-----------------------------

Navigate to the catalog of the board whose name you want to change and click on the
Admin link in the menu bar. You can then enter a new name for the board, change the
maximum number of allowed threads, as well as change the rules specific to the board.


Updating to a new version of Maniwani
-------------------------------------

For Docker-based deployments, after downloading the new container, run the `update`
command on the Maniwani container, which could either be something like `docker-compose run maniwani update`
if you're using a `docker-compose`-based deployment, or `docker run dangerontheranger/maniwani update` otherwise.
If your deployment does not use Docker, run `update.py` after downloading the latest version of Maniwani.
