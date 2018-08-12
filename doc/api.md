Maniwani REST API v1
====================

Basics
------

As of the latest revision of Maniwani, no authentication of any kind is
required to use the API. Simply point `curl` or your custom client at
the endpoint of your choice. If there's something on the website that you find you
cannot accomplish with REST, submit an issue report (or better yet, a pull request) - one
of the primary goals of Maniwani is 1:1 feature parity between the web and REST frontends.


Reading the firehose
--------------------

**Endpoint**: `/api/v1/firehose`

**Method**: `GET`

The firehose is the 10 most recently-bumped threads on the site regardless of
which board they came from. This endpoint currently takes no parameters; see the
section on reading catalogs for the format of the response.


Reading a catalog
-----------------

**Endpoint**: `/api/v1/<board ID>/catalog`

**Method**: `GET`

The catalog is the group of active threads belonging to the board with the given
ID, in descending order by most recent bump (most recent first). The response is
an array with each element representing a single thread, like so:

```
[
	{
		"body":"Everything should work as normal, though.",
		"id":1,
		"last_updated":"Sun, 12 Aug 2018 06:16:02 GMT",
		"media":1,
		"num_media":3,
		"num_replies":2,
		"subject":"Let's put the new merged stuff through its paces.",
		"tags": [
		{"name":"general"},
		{"name":"gallery"}
		"views":9
	}
]
```

The `body` attribute of a thread contains the post body of the initial post. This
string possibly contains Markdown, and it is up to the API client to strip or parse
the potential Markdown within. `id` is the thread ID that can then be taken to another
endpoint to get the posts within. `last_updated` represents the time at which the thread
was last bumped. `media` contains the ID of the image/video in the initial post in the thread.
`num_media` contains the total sum of images and videos posted within the thread so far.
`num_replies` contains the number of replies to the thread. `subject` is the subject
line of the thread/initial post (both are one and the same). Note that `subject` can potentially
be an empty field. `tags` is an array containing zero or more dictionaries, each with
a single key called `name` with the value being the name for that tag. Lastly,
`views` contains the number of times the thread in question has been visited, either from
its REST endpoint or from the web frontend. 


Getting the list of all boards (board index)
--------------------------------------------

**Endpoint**: `/api/v1/boards`

**Method**: `GET`

This endpoint contains the board index; the list of all boards currently registered
on the site instance. On a stock Maniwani installation, the response will be something
like the following:

```
[
	{
		"id": 1,
		"name": "anime",
		"media": 5
	},
	{
		"id": 2,
		"name": "tech",
		"media": null
	},
	{
		"id": 3,
		"name": "meta",
		"media": null
	},
	{
		"id": 4,
		"name": "politics",
		"media": null
	},
	{
		"id": 5,
		"name": "gaming",
		"media": 4
	},
	{
		"id": 6,
		"name": "music",
		"media": null
	}
]
```

Each entry in the array represents a single board. `id` is the ID of the board in
question, with `name` being its human-readable name. `media` is the media ID of
the image or video posted in the most recently-bumped thread in the board.


Getting the posts in a thread
-----------------------------

**Endpoint**: `/api/v1/thread/<thread ID>`

**Method**: `GET`

Contacting this endpoint with a thread ID obtained through the catalog gives
a response similar to the following (other posts omitted for brevity):

```
[
	{
		"body": "Everything should work as normal, though.",
		"datetime": "Sun, 12 Aug 2018 06:16:02 GMT",
		"id": 1,
		"media": 1,
		"media_ext": "jpg",
		"poster": "217E",
		"replies": [2],
		"slip": null,
		"spoiler": null,
		"subject": "Let's put the new merged stuff through its paces.",
		"tags":[
			{"name": "general"},
			{"name": "gallery"}]
	}
]
```

The attributes for each post are similar to that returned for each thread
from the firehose or the catalog, so only attributes specific to this response
or those functioning in a different way will be mentioned here. `datetime`
describes the date and time of when the post was made. `id` here refers to post ID
and not thread ID. `media_ext` is the original extension of the attachment and
intended to give the client an idea of what kind of media is attached to the post
prior to downloading it. `poster` is a 4 character-long string of hexadecimal characters
used to identify posters in the thread; all posts made by the same IP in a given thread
will have the same `poster` attribute. `replies` is a potentially-empty array of replies
to the this post. `slip` is the ID of the slip that the post was made with, or `null`
otherwise. `spoiler` will be set to `true` if the poster marked the attached media
in the post as containing a spoiler of some kind. If the post is the first in the
thread and the thread was tagged, then it will also have the `tags` attribute with
the same format as mentioned in the section on catalogs.
