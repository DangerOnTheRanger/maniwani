Maniwani - an imageboard done right
===================================

Maniwani is a work-in-progress imageboard implementation using Flask.

Where does the name come from? I could tell you, but by that point
you'd [have been torn to pieces.](https://wikipedia.org/wiki/Katanagatari)

(Planned!) Features
-------------------

* Per-thread auto-generated IDs (with avatars!)
* Download all media files in a thread (batch download, gzipped tar and zip
  archive support planned)
* Push notification support for new posts/threads with Javascript enabled
* Graceful UI degradation if Javascript is *not* enabled
* REST API for 3rd-party clients
* Global WebM audio support, muted by default but user-configurable
