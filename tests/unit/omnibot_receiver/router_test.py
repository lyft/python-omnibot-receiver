import pytest

from omnibot_receiver.router import (
    OmnibotMessageRouter,
    OmnibotInteractiveRouter,
    OmnibotRouter,
    RouteAlreadyDefinedError,
    NoMatchedRouteError
)


class TestOmnibotMessageRouter(object):

    def test_command_route(self):
        message = {'args': 'ping', 'match_type': 'command'}
        message_with_args = {'args': 'ping test', 'match_type': 'command'}
        message_router = OmnibotMessageRouter()

        @message_router.route('ping', match_type='command')
        def ping(message):
            return 'pong'

        # Test extra defined routes
        with pytest.raises(RouteAlreadyDefinedError):
            @message_router.route('ping', match_type='command')
            def extra_ping(message):
                return 'pong'

        @message_router.route('ping .*', match_type='command')
        def ping_with_args(message):
            return 'extra pong'

        assert message_router.handle_message(message) == 'pong'
        assert message_router.handle_message(message_with_args) == 'extra pong'

    def test_add_message_rule_with_arg(self):
        message = {'args': 'find testuser', 'match_type': 'command'}
        message_router = OmnibotMessageRouter()

        def user_finder(message, user):
            return 'found {}'.format(user)

        message_router.add_message_rule('find <user>', 'command', user_finder)

        assert message_router.handle_message(message) == 'found testuser'

    def test_command_route_with_arg(self):
        message = {'args': 'find testuser', 'match_type': 'command'}
        message_router = OmnibotMessageRouter()

        @message_router.route('find <user>', match_type='command')
        def user_finder(message, user):
            return 'found {}'.format(user)

        assert message_router.handle_message(message) == 'found testuser'

    def test_regex_route(self):
        message = {'args': '123 hello abc', 'match_type': 'regex'}
        message_router = OmnibotMessageRouter()

        @message_router.route('123.*abc', match_type='regex')
        def regex_matcher(message):
            return message['args']

        # Test regex routing
        assert message_router.handle_message(message) == '123 hello abc'

    def test_multiple_route(self):
        command_message = {'args': '123', 'match_type': 'command'}
        regex_message = {'args': '123 hello abc', 'match_type': 'regex'}
        message_router = OmnibotMessageRouter()

        @message_router.route('123', match_type='command')
        @message_router.route('123.*abc', match_type='regex')
        def multiple_matcher(message):
            return message['args']

        assert message_router.handle_message(command_message) == '123'
        assert message_router.handle_message(regex_message) == '123 hello abc'

    def test_default_route(self):
        message = {'args': 'unknown', 'match_type': 'regex'}
        expected_ret = {'actions': [{
            'action': 'chat.postMessage',
            'kwargs': {
                'text': 'example message',
                'attachments': [{
                    'title': 'Commands:',
                    'fields': [{
                        'title': 'ping',
                        'value': 'A route to respond to pings.',
                        'short': False
                    }]
                }]
            }
        }]}

        message_router = OmnibotMessageRouter(help='example message')

        @message_router.route(
            'ping',
            match_type='command',
            help='A route to respond to pings.'
        )
        def ping(message):
            pass

        # Test routing to help, when no default route is set
        assert message_router.handle_message(message) == expected_ret

        message_router = OmnibotMessageRouter(
            help='example message',
            help_as_default=False
        )

        # Test missing default route
        with pytest.raises(NoMatchedRouteError):
            message_router.handle_message(message)

        @message_router.set_default()
        def default(message):
            return 'default message'

        # Test exception raising when multiple default routes are provided
        with pytest.raises(RouteAlreadyDefinedError):
            @message_router.set_default()
            def extra_default(message):
                pass

        # Test default routing
        assert message_router.handle_message(message) == 'default message'

        message_router = OmnibotMessageRouter(help='example message')

        @message_router.route(
            'ping',
            match_type='command',
            help='A route to respond to pings.'
        )
        @message_router.set_default()
        def default_with_command(message):
            return 'default message'

        # Test default routing when a command route is set too
        assert message_router.handle_message(message) == 'default message'

    def test_get_help(self):
        message = {'args': 'help', 'match_type': 'command'}
        expected_ret = {'actions': [{
            'action': 'chat.postMessage',
            'kwargs': {
                'text': 'example message',
                'attachments': [
                    {
                        'title': 'Commands:',
                        'fields': [{
                            'title': 'ping',
                            'value': 'A route to respond to pings.',
                            'short': False
                        }]
                    },
                    {
                        'title': 'Regex matches:',
                        'fields': [{
                            'title': '.*test.*',
                            'value': 'A test regex route.',
                            'short': False
                        }]
                    },
                ]
            }
        }]}
        message_router = OmnibotMessageRouter(help='example message')

        @message_router.route(
            'ping',
            match_type='command',
            help='A route to respond to pings.'
        )
        def ping(message):
            pass

        @message_router.route(
            '.*test.*',
            match_type='regex',
            help='A test regex route.'
        )
        def text_regex(message):
            pass

        # Test default help routing
        assert message_router.handle_message(message) == expected_ret

        @message_router.set_help()
        def help(message):
            return 'overriden help'

        # Test exception raising when multiple help routes are provided
        with pytest.raises(RouteAlreadyDefinedError):
            @message_router.set_help()
            def extra_help(message):
                pass

        # Test overriden help routing
        assert message_router.handle_message(message) == 'overriden help'

        message_router = OmnibotMessageRouter(help='example message')

        @message_router.route(
            'help',
            match_type='command',
            help='Help docs for this bot.'
        )
        @message_router.set_help()
        def help_with_command(message):
            return 'overriden help'

        # Test overriden help routing with a command added
        assert message_router.handle_message(message) == 'overriden help'

    def test_greedy_pattern_match(self):
        message1 = {'args': '1 to 2', 'match_type': 'command'}
        message2 = {'args': '1 to 2 to 3', 'match_type': 'command'}
        message_router = OmnibotMessageRouter()

        def a_to_b(message, a, b):
            return 'a is {0}, b is {1}'.format(a, b)

        message_router.add_message_rule('<a> to <b>', 'command', a_to_b)

        assert message_router.handle_message(message1) == 'a is 1, b is 2'
        assert message_router.handle_message(message2) == 'a is 1 to 2, b is 3'

    def test_non_greedy_pattern_match(self):
        message1 = {'args': '1 to 2', 'match_type': 'command'}
        message2 = {'args': '1 to 2 to 3', 'match_type': 'command'}
        message_router = OmnibotMessageRouter()

        def a_to_b(message, a, b):
            return 'a is {0}, b is {1}'.format(a, b)

        message_router.add_message_rule('<a?> to <b>', 'command', a_to_b)

        assert message_router.handle_message(message1) == 'a is 1, b is 2'
        assert message_router.handle_message(message2) == 'a is 1, b is 2 to 3'

class TestOmnibotInteractiveRouter(object):

    def test_interactive_route(self):
        event = {'callback_id': 'ping'}
        interactive_router = OmnibotInteractiveRouter()

        @interactive_router.route('ping')
        def ping(event):
            return 'pong'

        # Test extra defined routes
        with pytest.raises(RouteAlreadyDefinedError):
            @interactive_router.route('ping')
            def extra_ping(event):
                return 'pong'

        assert interactive_router.handle_interactive_component(event) == 'pong'

    def test_overriden_interactive_route(self):
        event1 = {'callback_id': 'ping'}
        event2 = {'callback_id': 'ping', 'type': 'dialog_submission'}
        interactive_router = OmnibotInteractiveRouter()

        @interactive_router.route('ping')
        def ping(event):
            return 'pong'

        @interactive_router.route('ping', event_type='dialog_submission')
        def dialog_ping(event):
            return 'dialog_pong'

        # Test extra defined routes
        with pytest.raises(RouteAlreadyDefinedError):
            @interactive_router.route('ping', event_type='dialog_submission')
            def extra_dialog_ping(event):
                return 'dialog_pong'

        assert interactive_router.handle_interactive_component(
            event1
        ) == 'pong'
        assert interactive_router.handle_interactive_component(
            event2
        ) == 'dialog_pong'

    def test_multiple_route(self):
        event1 = {'callback_id': '123'}
        event2 = {'callback_id': '345'}
        interactive_router = OmnibotInteractiveRouter()

        @interactive_router.route('123')
        @interactive_router.route('345')
        def multiple_matcher(event):
            return event['callback_id']

        assert interactive_router.handle_interactive_component(event1) == '123'
        assert interactive_router.handle_interactive_component(event2) == '345'

    def test_default_route(self):
        event = {'callback_id': 'unknown'}
        interactive_router = OmnibotInteractiveRouter()

        @interactive_router.route('ping')
        def ping(event):
            pass

        @interactive_router.set_default()
        def default(event):
            return 'default message'

        # Test exception raising when multiple default routes are provided
        with pytest.raises(RouteAlreadyDefinedError):
            @interactive_router.set_default()
            def extra_default(event):
                pass

        # Test default routing
        assert interactive_router.handle_interactive_component(
            event
        ) == 'default message'


class TestOmnibotRouter(object):

    def test_handle_event(self):
        message_router = OmnibotMessageRouter()
        interactive_router = OmnibotInteractiveRouter()
        router = OmnibotRouter(
            message_router=message_router,
            interactive_router=interactive_router,
        )
        event1 = {
            'omnibot_payload_type': 'message',
            'args': 'ping',
            'match_type': 'command'
        }
        event2 = {
            'omnibot_payload_type': 'interactive_component',
            'callback_id': 'ping'
        }

        @interactive_router.route('ping')
        def interactive_ping(event):
            return 'interactive pong'

        @message_router.route('ping')
        def message_ping(event):
            return 'message pong'

        assert router.handle_event(event1) == 'message pong'
        assert router.handle_event(event2) == 'interactive pong'
