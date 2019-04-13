Contributing to Maniwani
========================

This document details the steps a new contributor should go through when wanting to contribute to
Maniwani, in addition to some useful information to anyone looking to extend its functionality.


So, you want to...
-------------------

### Report a bug

Just use the issue tracker and tag your issue as a bug. Make sure you specify whether or not
you're running Maniwani inside Docker, and if you are, whether you're using `devmode` or
full production mode. If you're not using Docker, information about the OS you're running
Maniwani with (version, version of Python you're using, etc.) would be helpful. Information
about supporting infrastructure - what database you're using, what object store you're using,
are you using reCAPTCHA, captchouli, or no CAPTCHA - would also be helpful.

### Request a feature

This is another good fit for the issue tracker. Make sure you put as much detail into your
request as possible; this will prevent someone else from implementing it in a way different
than what you had in mind. Also, try to justify why you think the feature should be added to
Maniwani. How would it mesh with its existing feature set? Would it help set it apart from
other imageboard engines?

### Implement a feature

Code contributions are always a sight for sore eyes on any open-source project. That said,
try to open a feature request if you're implementing a feature that nobody has put in the
issue tracker yet; there's no guarantee a PR will be accepted no matter how much work has
been put into it if the feature hasn't been discussed on the issue tracker first! Maniwani
has no real set coding standard, but try to follow PEP8 where you can.


Architecture at a glance
------------------------

Maniwani's overall architecture roughly follows a MVC layout; data is stored in SQLAlchemy
schemas (which lie in the `model` directory) while being displayed to clients over either a REST
API (which can be found spread out among `/model*Resource.py`) or via a browser with Jinja2 templates,
which are located in `templates`. Routing - figuring out what URLs belong to which models, as well as
some residual glue logic - can be found in `blueprints`.

There are a couple other supporting directories:
* `build-helpers` - this contains files such as the Docker image's entrypoint, as well as some extra
  utilities such as a script to retrieve a static build of `ffmpeg`, in addition to containing the
  Dockerfile for running captchouli.
* `deploy-configs` - this directory holds the stock configuration files used when running `docker-compose.yml`,
  and can be used as a starting point for configuration of proper Maniwani deployments.
* `scss` - this contains the Sass stylesheets used for styling Maniwani.
  

Coding case studies
-------------------

This section details some examples of how one would go about making some hypothetical modifications to
the Maniwani codebase.

### Adding a new REST endpoint

The first order of business would be to write the backend for the endpoint, which would go into the
`model` directory; see the code of the other REST endpoints if you need more details on interacting
with SQLAlchemy/Flask-RESTful. The next step would be to add it to the REST API defined in `app.py`,
at which point everything should be good to go.

### Modifying the Markdown parser

Maniwani uses Python-Markdown under the hood for parsing Markdown, so extending Maniwani's Markdown
capabilities follows the standard [Python-Markdown approach](https://python-markdown.github.io/extensions/api/);
be sure to place your extension in the `model` directory. You'll then need to register your extension
inside of `model/Post.py`.

### Generating a migration

Generating a new database migration - necessary when modifying the schema - is currently a mildly
complicated process, unfortunately. You will need:
* A database bootstrapped with the old database version, prior to your modifications. Re-using
  `devmode.cfg` found under `deploy-configs/` can help with this.
* A way to access the `migrations/` directory and save changes/new files made inside of it.
  This is currently probably easiest by installing the Python prerequisites for Maniwani directly
  on your development system via `pipenv`.
After fulfilling the above requirements, run `pipenv run flask db migrate` to generate a new migration. You can
then commit the new migration to Git.
