import omnibot_receiver.response


class TestOmnibotResponse(object):

    def test_extend_response(self):
        ret = {'actions': [
            {'action': 'chat.postMessage', 'kwargs': {'text': 'test'}}
        ]}
        extend_ret = {'actions': [
            {'action': 'chat.postMessage', 'kwargs': {'text': 'test2'}}
        ]}
        expected_ret = {'actions': [
            {'action': 'chat.postMessage', 'kwargs': {'text': 'test'}},
            {'action': 'chat.postMessage', 'kwargs': {'text': 'test2'}}
        ]}
        omnibot_receiver.response.extend_response(ret, extend_ret)
        assert ret == expected_ret

    def test_get_simple_post_message(self):
        expected_ret = {'actions': [
            {'action': 'chat.postMessage', 'kwargs': {'text': 'test'}}
        ]}
        # Test simple case
        assert omnibot_receiver.response.get_simple_post_message(
            'test'
        ) == expected_ret

        expected_ret = {'actions': [
            {'action': 'chat.postMessage', 'kwargs': {
                'text': 'test',
                'omnibot_parse': ['all']
            }}
        ]}
        # Test case with omnibot_parse param
        assert omnibot_receiver.response.get_simple_post_message(
            'test',
            omnibot_parse=['all']
        ) == expected_ret

        expected_ret = {'actions': [
            {'action': 'chat.postMessage', 'kwargs': {
                'text': 'test',
                'thread_ts': None
            }}
        ]}
        # Test case with thread param
        assert omnibot_receiver.response.get_simple_post_message(
            'test',
            thread=False
        ) == expected_ret
