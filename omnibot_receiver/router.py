"""
.. module:: router
   :synopsis: A module for omnibot routing utilities.
"""
import re


class OmnibotRouter(object):

    """
    A generic omnibot router. The omnibot router can be used to map any type
    of message, to one of the configured routers.

    .. code-block:: python

        from omnibot_receiver.router import (
            OmnibotMessageRouter,
            OmnibotInteractiveRouter,
            OmnibotRouter,
        )

        message_router = OmnibotMessageRouter(
            help='This bot is used for pings and pongs.'
        )
        interactive_router = OmnibotInteractiveRouter()
        router = OmnibotRouter(
            message_router=message_router,
            interactive_router=interactive_router
        )

    This makes it possible to route all omnibot payloads via a single function.

    .. code-block:: python

          from bot_location import router

          @flask_app.route('/api/v1/bot', methods=['POST'])
          def pingbot_route():
              message = request.get_json()
              ret = router.handle_message(message)
              return jsonify(ret)
    """

    def __init__(self, message_router=None, interactive_router=None):
        """
        Init function for OmnibotRouter.

        Returns:

            An instance of OmnibotRouter
        """
        self.message_router = message_router
        self.interactive_router = interactive_router

    def handle_event(self, event):
        """
        For the given event, route the event to the relevant configured router
        and to the registered function that matches the event in that router.

        Args:

            event (dict): An event sent by omnibot.

        Returns:

            A dict with an `actions` attribute that contains a list of slack
            actions to be returned to omnibot. See
            `slack API methods docs <https://api.slack.com/methods>`_ for
            actions and kwargs. Example:

            .. code-block:: json

                {'actions': [
                    {'action': 'chat.postMessage',
                        'kwargs': {
                            {'text': 'Hello World!'}
                        }
                    },
                    {
                        'action': 'reactions.add',
                        'kwargs': {
                            'name': 'heart'
                        }
                    }
                ]}
        """
        omnibot_payload_type = event.get('omnibot_payload_type')
        if (self.message_router and
                omnibot_payload_type in {'message', 'reaction'}):
            return self.message_router.handle_message(event)
        elif (self.interactive_router and
              omnibot_payload_type == 'interactive_component'):
            return self.interactive_router.handle_interactive_component(event)
        else:
            raise UnsupportedPayloadError(
                'Payload type currently unsupported'
            )


class OmnibotMessageRouter(object):

    """
    An omnibot message router. The omnibot router can be used to map commands
    and regex matches to functions in your code.

    Every route will be passed the message that comes from omnibot as the
    first argument. It's possible to define multiple routes for a single
    function, but it's important to remember that only a single default route
    can be defined. For details on routing, see
    :func:`omnibot_receiver.router.OmnibotMessageRouter.route()`. Rules can
    also be specified more directly via
    :func:`omnibot_receiver.router.OmnibotMessageRouter.add_message_rule()`.
    Here's a basic routing example:

    .. code-block:: python

        from omnibot_receiver.router import OmnibotMessageRouter

        message_router = OmnibotMessageRouter(
            help='This bot is used for pings and pongs.'
        )

        @message_router.route(
            'ping',
            match_type='command',
            help='Responds to pings with pongs'
        )
        @message_router.route(
            '.*ping.*',
            match_type='regex',
            help='Responds to messages of pings with pongs'
        )
        def ping(message):
            ret = {'actions': []}
            ret['actions'].append({
                'action': 'chat.postMessage',
                'kwargs': {'text': 'pong'}
            })
            return ret

    If you want the bot to default any unrecognized message to a function,
    you can set a function as a default route:

    .. code-block:: python

        @message_router.set_default()
        def unknown(message):
            ret = {'actions': []}
            ret['actions'].append({
                'action': 'chat.postMessage',
                'kwargs': {'text': 'Unrecognized command.'}
            })
            return ret

    If no default route is defined, OmnibotMessageRouter will automatically
    route unmatched messages to the help documentation. If you want unmatched
    messages to be ignored, you can initialize OmnibotMessageRouter with
    help_as_default as False:

    .. code-block:: python

        from omnibot_receiver.router import OmnibotMessageRouter

        message_router = OmnibotMessageRouter(
            help='This bot is used for pings and pongs.',
            help_as_default=False
        )

    The router is roughly modeled after Flask, so it's possible to define
    variables to capture in the route. For example, below we're capturing
    a part of the command string (user), and it's being passed into the
    function.

    .. code-block:: python

        @message_router.route(
            'find <user>',
            match_type='command',
            help='Find info about a user.'
        )
        def find_user(message, user):
            ret = {'actions': []}
            ret['actions'].append({
                'action': 'chat.postMessage',
                'kwargs': {'text': 'example'}
            })
            return ret

    The expected return structure of your routed functions is:

    .. code-block:: json

        {'actions': [
            {'action': '<slack_api_action>',
                'kwargs': {
                    'arg_to_slack_api_action': 'arg_value'
                }
            }
        ]}

    Note in the above that you can return a list of actions, allowing you to
    do things like post a response to a thread, post to a channel, add
    reactions to a message, etc.

    By default omnibot-receiver will auto-generate help documentation for your
    bot from the help parameters of the OmnibotMessageRouter class and the
    defined routes. It's possible to override this, by setting the help:

    .. code-block:: python

        @message_router.set_help()
        def help(message):
            # This is what gets returned by default.
            return message_router.get_help(message)

    Setting help doesn't route a `help` command to your help function, if you
    wish to do so, add a command to the function:

    .. code-block:: python

        @message_router.route(
            'help',
            match_type='command',
            help='Help for this bot'
        )
        @message_router.set_help()
        def help(message):
            # This is what gets returned by default.
            return message_router.get_help(message)

    Once your routes are defined, you can send an omnibot message to the bot,
    it'll route it to the correct function, and you'll get a return, which
    you can return back to omnibot:

    .. code-block:: python

        ret = message_router.handle_message(message)
        return jsonify(ret)
    """

    def __init__(self, help='', help_as_default=True):
        """
        Init function for OmnibotMessageRouter.

        Args:

            help (str): Help documentation that will be shown as the default
            help message header text.
            help_as_default (bool): Whether or not the bot will use the help
            route as a default fallback, if a default route isn't set.

        Returns:

            An instance of OmnibotMessageRouter
        """
        self.help_message = help
        self.help_as_default = help_as_default
        self.help_route = None
        self.default_route = None
        self.routes = {
            'command': [],
            'regex': [],
            'reaction': [],
        }

    @staticmethod
    def _get_route_pattern(route):
        """
        Generate a regex from a route definition.

        Args:

            route (str): The route to compile into a regex.

        Returns:

            _sre.SRE_Pattern (a compiled regex)
        """
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route)
        route_regex = re.sub(r'(<\w+)\?>', r'(?P\1>.+?)', route_regex)
        return re.compile("^{}$".format(route_regex))

    def set_help(self, **kwargs):
        """
        Register a function to render help documentation. Note that this is
        not a route, but is the function that renders the help only. You must
        register a help command to route to this function.
        """
        def decorator(f):
            if self.help_route:
                raise RouteAlreadyDefinedError(
                    'A help route has already been set.'
                )
            self.help_route = f
            return f

        return decorator

    def set_default(self, **kwargs):
        """
        Register a route as a default route. If a message isn't matched by
        another registered route, it'll fall back to this route. Only a single
        route can be defined as a default; setting two defaults will result in
        a RouteAlreadyDefinedError being raised.
        """
        def decorator(f):
            if self.default_route:
                raise RouteAlreadyDefinedError(
                    'A default route has already been set.'
                )
            self.default_route = f
            return f

        return decorator

    def add_message_rule(self, rule, match_type, route_func, help=''):
        """
        Register a function to be called for messages matching the given rule.

        Args:

            rule (str): A regex to match messages against.
            match_type (str): The type of message this route should match
            against::

                    command  -- Match against messages directed at this bot.
                    regex    -- Match against messages in a channel that have
                                been targeted at this bot by omnibot.
                    reaction -- Match against reactions towards items
                                made by this bot.

            route_func (function): The function to call when serving this route
            **kwargs (dict): Keyword arguments (see below for more info)

        Keyword Args:

            help (str): Help text for this route, to be included with the help
            docs generated from
            :func:`omnibot_receiver.router.OmnibotMessageRouter.get_help()`

        Usage:

        .. code-block:: python

            from omnibot_receiver.router import OmnibotMessageRouter

            message_router = OmnibotMessageRouter(
                help='This bot is used for pings and pongs.'
            )

            def ping(message):
                # return some actions

            message_router.add_message_rule(
                'ping',
                'command',
                ping,
                help='Responds to pings'
            )
        """
        help_text = '{}:{}'.format(rule, help)

        route_pattern = self._get_route_pattern(rule)
        for _pattern, _, _ in self.routes[match_type]:
            if route_pattern == _pattern:
                raise RouteAlreadyDefinedError(
                    '{} is already defined for match type {}.'.format(
                        rule,
                        match_type
                    )
                )
        self.routes[match_type].append((route_pattern, help_text, route_func))

    def route(self, rule, **kwargs):
        """
        Register a route for this bot via a decorator.

        Args:

            rule (str): A regex to match messages against.
            **kwargs (dict): Keyword arguments (see below for more info)

        Keyword Args:

            match_type (str): The type of message this route should match
            against::

                    command -- Match against messages directed at this bot.
                    regex   -- Match against messages in a channel that have
                               been targetted at this bot by omnibot.

            help (str): Help text for this route, to be included with the help
            docs generated from
            :func:`omnibot_receiver.router.OmnibotMessageRouter.get_help()`
        """

        def decorator(f):
            self.add_message_rule(
                rule,
                kwargs.pop('match_type', 'command'),
                f,
                help=kwargs.pop('help', ''),
            )
            return f

        return decorator

    def _get_route_match(self, text, match_type):
        """
        For the given text and match type, find and return parsed arguments
        and a function for a registered route.

        Args:

            text (str): The text to match against.
            match_type (str): The match type to use for finding routes (see
            :func:`omnibot_receiver.router.OmnibotMessageRouter.route()`)
        """
        for route_pattern, _, view_function in self.routes[match_type]:
            m = route_pattern.match(text)
            if m:
                return m.groupdict(), view_function

        return None

    def get_help(self, message, **kwargs):
        """
        Autogenerate and return a help message for this router based on the
        commands and regexes registered.

        Args:

            message (dict): An omnibot message of type `help`.
            **kwargs (dict): A dict provided for compatibility with the
            calling function.

        Returns:

            A dict of action lists to be returned to omnibot. Example:

            .. code-block:: json

                {
                    'actions' = [{
                        'action': 'chat.postMessage',
                        'kwargs': {
                            'text': 'example message',
                            'attachments': [{
                                'title': 'Commands:',
                                'fields': [{
                                    'title': 'help',
                                    'value': 'A help command.',
                                    'short': False
                                }]
                            }]
                        }
                    }]
                }
        """
        ret_action = {
            'action': 'chat.postMessage',
            'kwargs': {'text': self.help_message, 'attachments': []}
        }
        ret = {'actions': [ret_action]}
        if self.routes['command']:
            fields = []
            for _, help_text, _ in self.routes['command']:
                action, text = help_text.split(':', 1)
                fields.append({
                    'title': action,
                    'value': text,
                    'short': False
                })
            ret_action['kwargs']['attachments'].append({
                'title': 'Commands:',
                'fields': fields
            })
        if self.routes['regex']:
            fields = []
            for _, help_text, _ in self.routes['regex']:
                action, text = help_text.split(':', 1)
                fields.append({
                    'title': action,
                    'value': text,
                    'short': False
                })
            ret_action['kwargs']['attachments'].append({
                'title': 'Regex matches:',
                'fields': fields
            })
        return ret

    def _get_help_func(self):
        if self.help_route:
            return self.help_route
        else:
            return self.get_help

    def handle_message(self, message):
        """
        For the given message, route the message to any routes registered that
        match its attributes, and return a list of actions for omnibot.

        Args:

            message (dict): A message sent by omnibot.

        Returns:

            A dict with an `actions` attribute that contains a list of slack
            actions to be returned to omnibot. See
            `slack API methods docs <https://api.slack.com/methods>`_ for
            actions and kwargs. Example:

            .. code-block:: json

                {'actions': [
                    {'action': 'chat.postMessage',
                        'kwargs': {
                            {'text': 'Hello World!'}
                        }
                    },
                    {
                        'action': 'reactions.add',
                        'kwargs': {
                            'name': 'heart'
                        }
                    }
                ]}
        """
        match_type = message['match_type']
        args = message.get('args', '')
        route_match = self._get_route_match(args, match_type)
        if route_match:
            kwargs, view_function = route_match
            return view_function(message, **kwargs)
        else:
            # No match, fall back to the default route, if defined
            if self.default_route:
                return self.default_route(message)
            else:
                if self.help_as_default:
                    help_func = self._get_help_func()
                    return help_func(message)
                else:
                    # No default route, raise an exception.
                    raise NoMatchedRouteError(
                        'No route "{}" for match_type "{}" and no default'
                        'route set.'
                        .format(args, match_type)
                    )


class OmnibotInteractiveRouter(object):

    """
    An omnibot interactive component event router. This router can map
    interactive component event callback IDs to functions.

    Every route will be passed the event that comes from omnibot as the
    first argument. It's possible to define multiple routes for a single
    function, but it's important to remember that only a single default route
    can be defined. For details on routing, see
    :func:`omnibot_receiver.router.OmnibotInteractiveRouter.route()`.
    Here's a basic routing example:

    .. code-block:: python

        from omnibot_receiver.router import OmnibotInteractiveRouter

        interactive_router = OmnibotInteractiveRouter()

        @interactive_router.route('ping_callback')
        def ping(event):
            ret = {'actions': []}
            ret['actions'].append({
                'action': 'chat.postMessage',
                'kwargs': {'text': 'pong'}
            })
            return ret

    It's possible for multiple types of interactive components to share the
    same callback_id. By default, route will route all events to the defined
    function, but if you'd like to split specific event types out, you can
    specify a separate route with the event_type. Here's a routing example:

    .. code-block:: python

        @interactive_router.route(
            'ping_callback',
            event_type='dialog_submission'
        )
        def ping(event):
            ret = {'actions': []}
            ret['actions'].append({
                'action': 'chat.postMessage',
                'kwargs': {'text': 'pong'}
            })
            return ret

    If you want the bot to default any unrecognized event to a function,
    you can set a function as a default route:

    .. code-block:: python

        @interactive_router.set_default()
        def unknown(event):
            ret = {'actions': []}
            ret['actions'].append({
                'action': 'chat.postMessage',
                'kwargs': {'text': 'Unrecognized callback.'}
            })
            return ret

    The expected return structure of your routed functions is:

    .. code-block:: json

        {'actions': [
            {'action': '<slack_api_action>',
                'kwargs': {
                    'arg_to_slack_api_action': 'arg_value'
                }
            }
        ]}

    Note in the above that you can return a list of actions, allowing you to
    do things like post a response to a thread, post to a channel, add
    reactions to a message, etc.

    Once your routes are defined, you can send an omnibot event to the bot;
    it'll route it to the correct function, and you'll get a return, which
    you can return back to omnibot:

    .. code-block:: python

        ret = interactive_router.handle_interactive_component(event)
        return jsonify(ret)
    """

    def __init__(self):
        """
        Init function for OmnibotInteractiveRouter.

        Returns:

            An instance of OmnibotInteractiveRouter
        """
        self.default_route = None
        self.routes = {'__all': []}

    def set_default(self, **kwargs):
        """
        Register a route as a default route. If an event isn't matched by
        another registered route, it'll fall back to this route. Only a single
        route can be defined as a default; setting two defaults will result in
        a RouteAlreadyDefinedError being raised.
        """
        def decorator(f):
            if self.default_route:
                raise RouteAlreadyDefinedError(
                    'A default route has already been set.'
                )
            self.default_route = f
            return f

        return decorator

    def add_event_callback(
        self,
        callback_id,
        route_func,
        event_type=None,
    ):
        """
        Register a function to be called for messages matching the given rule.

        Args:

            callback_id (str): A callback_id to match events against.
            event_type (str): The event type of interactive component, to match
            against.
            route_func (function): The function to call when serving this route

        Usage:

        .. code-block:: python

            from omnibot_receiver.router import OmnibotInteractiveRouter

            interactive_router = OmnibotInteractiveRouter()

            def ping(event):
                # return some actions

            interactive_router.add_event_callback('ping_callback', ping)

        """
        if event_type is None:
            event_type = '__all'
        if event_type not in self.routes:
            self.routes[event_type] = []
        for _callback_id, _ in self.routes[event_type]:
            if callback_id == _callback_id:
                raise RouteAlreadyDefinedError(
                    '{} is already defined'.format(callback_id)
                )
        self.routes[event_type].append((callback_id, route_func))

    def route(self, callback_id, **kwargs):
        """
        Register a route for this bot via a decorator.

        Args:

            callback_id (str): A callback_id to match messages against.
        """

        def decorator(f):
            try:
                event_type = kwargs.pop('event_type')
            except KeyError:
                event_type = None
            self.add_event_callback(
                callback_id,
                f,
                event_type=event_type,
            )
            return f

        return decorator

    def _get_route_match(self, callback_id, event_type):
        """
        For the given callback_id, find and return the function for a
        registered route.

        Args:

            text (str): The text to match against.
        """
        # First check for a route based on the event_type.
        for _callback_id, view_function in self.routes.get(event_type, []):
            if callback_id == _callback_id:
                return view_function
        # If there isn't an event_type override for routes, look in the __all
        # bucket.
        for _callback_id, view_function in self.routes.get('__all'):
            if callback_id == _callback_id:
                return view_function

        return None

    def handle_interactive_component(self, event):
        """
        For the given event, route the event to any routes registered that
        match the callback id, and return a list of actions for omnibot.

        Args:

            event (dict): An interactive event sent by omnibot.

        Returns:

            A dict with an `actions` attribute that contains a list of slack
            actions to be returned to omnibot. See
            `slack API methods docs <https://api.slack.com/methods>`_ for
            actions and kwargs. Example:

            .. code-block:: json

                {'actions': [
                    {'action': 'chat.postMessage',
                        'kwargs': {
                            {'text': 'Hello World!'}
                        }
                    },
                    {
                        'action': 'reactions.add',
                        'kwargs': {
                            'name': 'heart'
                        }
                    }
                ]}
        """
        callback_id = event.get('callback_id')
        event_type = event.get('type')
        view_function = self._get_route_match(callback_id, event_type)
        if view_function:
            return view_function(event)
        else:
            # No match, fall back to the default route, if defined
            if self.default_route:
                return self.default_route(event)
            else:
                # No default route, raise an exception.
                raise NoMatchedRouteError(
                    'No route "{}" and no default route set.'.format(
                        callback_id
                    )
                )


class RouteAlreadyDefinedError(Exception):
    pass


class NoMatchedRouteError(Exception):
    pass


class UnsupportedPayloadError(Exception):
    pass
