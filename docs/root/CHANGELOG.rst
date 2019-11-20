Changelog
=========

3.0.0
-----

This is a breaking release, as :class:`omnibot_receiver.router.OmnibotRouter` is now a generic routing class that can route events to instances of :class:`omnibot_receiver.router.OmnibotMessageRouter` or :class:`omnibot_receiver.router.OmnibotInteractiveRouter`.

* Moved :class:`omnibot_receiver.router.OmnibotRouter` to :class:`omnibot_receiver.router.OmnibotMessageRouter`
* Added :class:`omnibot_receiver.router.OmnibotInteractiveRouter`, which can be used to route interactive messages, via callbacks.
* Changed :class:`omnibot_receiver.router.OmnibotRouter` to be a generic event router, which can be initialized with message and interactive routers. This makes it possible to configure a single flask route that accepts all types of omnibot payloads, and have them automatically routed to the configured message or interactive router routes.
* Updated :func:`omnibot_receiver.response.get_simple_post_message` to accept an argument to mark a message as ephemeral.
* Added :func:`omnibot_receiver.response.get_simple_response` to send back a simple reponse to omnibot, for interactive message or slash command responses.

2.0.0
-----

* Move default and help match types to separate functions, `set_default` and `set_help`. This simplifies the code and makes it clearer what's happening, since it's not necessary to send unused args into the decorators.
* Add custom exceptions `RouteAlreadyDefinedError` and `NoMatchedRouteError`, rather than returning `ValueError` when failing. `RouteAlreadyDefinedError` is used when a help or default decorator is set more than once. `NoMatchedRouteError` is used when a message is received that has no matching routes and the router was configured not to fall back to help documentation.

1.1.0
-----

* Have the router default unmatched routes to help, if no default is defined. This can be disabled through an arg on init. See :class:`omnibot_receiver.router.OmnibotRouter` for more info.
* Added a new :mod:`omnibot_receiver.response` module for handling common responses.

1.0.0
-----

* Refactor :class:`omnibot_receiver.router.OmnibotRouter` to provide a full omnibot response through help, adding support for `help` match\_types for routes.

0.1.0
-----

* Initial commit
* Add support for :class:`omnibot_receiver.router.OmnibotRouter`
