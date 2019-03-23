Deploying Maniwani
==================

This document primarily deals with the ins and outs of deploying a production instance
of Maniwani in the wild, and any configuration options that you should be aware of
when deploying a production instance. The instructions and notes in this document
are largely based on the deployment of [Futatsu](http://futatsu.org), but should
be relevant to any Maniwani instance.


Production environment requirements
-----------------------------------

Besides obviously Maniwani, your production environment should have a couple
other pieces of software installed:

* A SQL database. PostgreSQL is the primary supported platform, but SQLite works as
  well, and will probably suffice if you're fine with hosting Maniwani and the database
  on the same machine. Other databases may work, but are unsupported.
* An S3 instance or S3-compatible object store. Minio is known to work and is the
  S3-compatible store used when using the sample `docker-compose.yml` in Maniwani's
  Github repository, while Futatsu uses an actual Amazon S3 instance. Strictly speaking,
  an S3 store isn't necessary, but most serious deployments should use it over the
  filesystem storage backend for performance reasons.
* Docker is recommended for deploying Maniwani itself, since it removes the need
  to install and manage prerequisites for Maniwani in addition to making updating
  to newly-released versions a breeze. The rest of this guide assumes usage of Docker.
* A reverse proxy is also recommended, but is not strictly necessary; the default uWSGI
  configuration bundled with Maniwani in `deploy-configs` assumes a WSGI-capable reverse
  proxy. Futatsu uses nginx, but Apache with `mod_wsgi` should work as well. The `nginx.conf`
  located in `deploy-configs` - the one used when running the stack defined by the sample
  `docker-compose.yml` - should work with no modification if nginx and Maniwani live
  on the same machine.
* If you want to use [captchouli](https://github.com/bakape/captchouli) for serving CAPTCHAs,
  you'll need to have an instance of it running in a place Maniwani can access, ideally on the
  same machine as Maniwani itself or otherwise hidden from public view - at present, captchouli
  is not intended to be public-facing.


Configuring Maniwani
--------------------

Maniwani can be configured for production entirely by modifying the files present in
the `deploy-configs` directory; you have the option of modifying the files from an
archive of Maniwani's source and then building and deploying a Docker image from that,
or you can copy the directory out, make the necessary modifications for your environment, and
then mount your directory to `/maniwani/deploy-configs` when running Maniwani under
Docker; the latter is the recommended approach and the one Futatsu takes. In particular,
you should definitely modify `maniwani.cfg`, `bootstrap-config.json`, and `index-greeting.html`,
but `uwsgi.ini` is available if you need to modify the way the uWSGI application server
hosts Maniwani. The specifics of uWSGI's configuration settings are outside the scope of this
document, but the default supplied with Maniwani should be sufficient for most deployments.

`maniwani.cfg` is the file that Maniwani refers to for database/S3 endpoint info as well as
credentials, in addition to a couple other configuration settings. It's a full-blown Python
file, and while you shouldn't need any logic capabilities, you should be aware that you can
take advantage of its Python nature. Most of the options are relatively self-explanatory,
but a brief description of each follows:

* `INSTANCE_NAME` - this string controls the name of the deployed Maniwani instance, which
  will show up in the navbar and a couple other places across the site.
* `SQLALCHEMY_DATABASE_URI` - this is the URI of your SQL database. The basic format
  is `<protocol>://<username>:<password>@<hostname>/<database>`, but consult SQLAlchemy's
  documentation if you need more information.
* `STORAGE_PROVIDER` - this variable indicates whether static assets are stored in an S3
  or otherwise S3-compatible object store or located locally on the same filesystem as
  Maniwani itself. For S3, this should be set to `"S3"`; for the filesystem backend,
  choose `"FOLDER"`. In a production environment, an S3 store is almost certainly the better
  option.
* `S3_ENDPOINT` - a string storing the endpoint URL for your S3 store that Maniwani should contact.
  Both HTTP and HTTPS will work, as long as your S3 store supports them. This and other S3-specific
  configuration options are not required if you use the filesystem storage backend.
* `S3_ACCESS_KEY` - a string containing the access key for the S3 store.
* `S3_SECRET_KEY` - a string containing the secret key for the s3 store.
* `S3_UUID_PREFIX` - Amazon, among S3 providers, requires that bucket names be globally unique across
  their service. This is an optional string that Maniwani will prepend to the names of the buckets
  it creates to ensure uniqueness. There is no set restriction on the contents of this string outside
  of what would constitute part of a valid URL.
* `CDN_REWRITE` - this is an optional string that, if present, will be used as a template by the
  S3 backend when outputting links to media. The [named placeholders](https://pyformat.info/#named_placeholders)
  supplied by Maniwani are: `ENDPOINT`, `BUCKET_UUID`, `BUCKET`, and `PATH`. `PATH` is the path to the
  resource (and does not begin with a `/`), while `BUCKET_UUID` is equal to `S3_UUID_PREFIX`, if it is
  present.
* `SERVE_STATIC` - this is a boolean that indicates whether Maniwani should serve up CSS/JS/other
  static non-attachment assets itself (if set to `True`) or let the S3 store handle it (if set
  to `False`). This should be set to `False` for a production deploymenet.
* `SERVE_REST` - if `True`, REST endpoints will be served by Maniwani. Note that ideally, the REST API for
  your Maniwani installation is protected with HTTPS, since Maniwani uses HTTP Basic for authentication and
  authorization.
* `MAX_CONTENT_LENGTH` - this is an integer detailing the largest attachment Maniwani should accept
  in bytes. Note that your reverse proxy should be set up to not deny any requests smaller than this;
  if you're copying or following along with the `nginx.conf` bundled with Maniwani under the `deploy-configs`
  directory, you should be okay.
* `CAPTCHA_METHOD` - this as an optional string indicating which CAPTCHA provider Maniwani should attempt to
  use; valid values are `"RECAPTCHA"` and `"CAPTCHOULI"`.
* `RECAPTCHA_SITE_KEY` - the site key that you can find on your reCAPTCHA dashboard.
* `RECAPTCHA_SECRET_KEY` - the secret key that you can find on your reCAPTCHA dashboard. You don't need to
  supply these options unless `CAPTCHA_METHOD` has been set to `"RECAPTCHA"`, obviously.
* `CAPTCHOULI_URL` - an URL specifying where the captchouli server has been set up. Only required if
  `CAPTCHA_METHOD` has been set to `"CAPTCHOULI"`.

`bootstrap-config.json` is the file used upon bootstrapping Maniwani for the first time to set up any boards,
configure any initial slips (usually admin/moderator roles, but they don't have to be) and set up any special
tags, among other things. There are a couple different top-level settings:

* `default_threadlimit` - this is an integer describing the number of threads each board should hold. This can
  be overridden later on in the file on a per-board basis, and set on a per-board basis after deployment via
  the admin interface.
* `default_mimetypes` - this is a regular expression that should match the MIME types of attachments that are
  valid across all boards in your deployed instance. You can modify this setting on a per-board basis after
  deployment via the admin interface, in addition to setting extra valid MIME types on a per-board basis later
  on in this file.

Next is `boards`, which is an array containing a list of objects representing each board that Maniwani should
set up. The keys valid in each object are:

* `name` - this is simply a string containing the name of the board in question. Ideally, each name should be
  around 6-7 characters max to fit best with Maniwani's UI. You can modify the name of the board from the admin
  interface after deployment, as well.
* `extra_mimetypes` - this is a regular expression matching any additional MIME types that should be valid
  for this board. Again, valid MIME types can be set after deployment on a per-board basis via the admin
  interface. This is an optional setting and doesn't have to be provided.
* `rules` - this is an optional string containing the path relative to the `deploy-configs` directory
  to a Markdown file listing rules specific to this board. HTML is not escaped unlike HTML embedded in posts
  on the site, so you can mix in HTML if Markdown proves too limiting for some reason.
* `threadlimit` - this is an optional integer detailing how many threads at max this board should contain.
  If not given, `default_threadlimit` is used instead. Like the other board options, it is modifiable
  from the admin interface after deployment.

The next key is `slips`, which is an array defining any initial slips that should be set up. While slips can be
created after deployment, this file is currently the only way to give a slip admin privileges, so admin slips
should be created here. The keys in each object in `slips` are: 

* `username` - the username for the slip in question.
* `password` - the password for the slip.
* `is_mod` - an optional boolean, that if set to `true` will give moderator privileges to the slip.
* `is_admin` - an optional boolean that will grant admin privileges if set to `true`.

Finally, the last key is `tags`, which is an array of objects that defines any special tags. Users can tag threads,
and the first tag in their list can modify the appearance of their thread in the catalog, and in the future could
modify other aspects of their thread as well. The keys for each entry in `tags` are:

* `tag` - the name of the tag. By convention, Maniwani tags are all lowercase with no spaces, though spaces and
  mixed cases are technically allowed.
* `bgstyle` - the CSS class given to the background of threads with this tag as the first tag in the catalog
  and firehose. This can be a Bootstrap class or a custom CSS class if you have modified Maniwani's CSS.
* `textstyle` - the CSS class given to the text of threads with this tag as the first in the catalog and
  firehose. This can also be a Bootstrap or custom CSS class.
  
Since this is a lot of info to take in, here's an example `bootstrap-config.json` practically identical to the
one used with Futatsu:

```
{
	"default_threadlimit": 100,
	"default_mimetypes": "image/jpeg|image/png|image/gif|image/webp|video/webm",
	"boards": [
		{
			"name": "fate",
			"rules": "fate-rules.md"
		},
		{
			"name": "code",
			"rules": "code-rules.md",
			"extra_mimetypes": "text/*"
		},
		{
			"name": "draw",
			"rules": "draw-rules.md"
		},
		{
			"name": "write",
			"rules": "write-rules.md",
			"extra_mimetypes": "text/*"
		},
		{
			"name": "sub",
			"rules": "sub-rules.md",
			"extra_mimetypes": "text/*"
		},
		{
			"name": "meta",
			"rules": "meta-rules.md"
		},
		{
			"name": "life",
			"rules": "life-rules.md"
		}
	],
	"slips": [
		{
			"username": "moot",
			"password": "hunter2",
			"is_admin": true
		}
	],
	"tags": [
		{
			"tag": "question",
			"bgstyle": "bg-secondary",
			"textstyle": "text-light"
		}
	]
}
```

The last file that you should probably consider modifying is the `index-greeting.html`
file that will be displayed on the index page if the visitor is not logged into a slip.
For instance, Futatsu has an `index-greeting.html` file that looks like this:

```
<div class="jumbotron">
    <h1 class="display-4">Futatsu</h1>
    <p class="lead">The maker's haven</p>
    <hr class="my-4">
    <p>Futatsu is an imageboard intended to promote and discuss all different kinds of self-made digital content! Come
		and discuss best practices for programming, drawing, and more, get feedback on your
		work-in-progress, or show off your latest creation. Below, you can find the most
	recently-updated threads on the site.</p>
</div>
```


Configuring your production environment
---------------------------------------

Running Maniwani's bootstrap script should be all that's necessary to set up your
production database and S3 store. Utilizing Docker and the mounting strategy mentioned earlier in
this document, once your SQL and S3 servers are running, you can run this to bootstrap your database
and S3 store:

```
docker -v /path/to/production/deploy-configs:/maniwani/deploy-configs run dangerontheranger/maniwani bootstrap
```

This will create a file called `secret` in your production `deploy-configs` directory; make sure that
you keep this file along with the rest of the files in the directory.

Depending on your specific setup - and definitely in the case of an actual S3 instance,
[CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) will have to be set up in
order for static assets to be properly retrieved. The following AWS S3 configuration should suffice,
which you should set on whichever bucket holds your static assets, though you'll need to wait until
after Maniwani has bootstrapped your buckets:

```
<CORSConfiguration>
 <CORSRule>
   <AllowedOrigin>*</AllowedOrigin>
   <AllowedMethod>GET</AllowedMethod>
 </CORSRule>
</CORSConfiguration>
```

If you need help figuring out where to set the CORS policy, consult Amazon's S3 documentation.


Running Maniwani
----------------

Running Maniwani is highly dependent on how you've organized things in your particular production
environment - whether you're using `docker-compose` or some other tool, etc. - but in essence comes
down to more or less running `docker run dangerontheranger/maniwani` while ensuring the other
pieces of your stack are also executing. If you went with the directory mount option for your custom
configuration files, don't forget to mount that with `--mount` or `-v` before running the container.
