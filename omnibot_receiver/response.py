"""
.. module:: response
   :synopsis: A module for simplifying frequently used responses.
"""


def extend_response(resp, extend_resp):
    """
    Extend an omnibot response dict structure.

    Args:

        resp (dict): An omnibot response dict.
        extend_resp (dict): An omnibot response dict.

    Returns:

        An omnibot response dict with the actions extended; example:

        .. code-block:: json

            {
                'actions': [
                    {
                        'action': 'chat.postMessage',
                        'kwargs': {
                            'text': 'example'
                        }
                    },
                    {
                        'action': 'chat.postMessage',
                        'kwargs': {
                            'text': 'extended example'
                        }
                    }
                ]
            }
    """
    resp['actions'].extend(extend_resp['actions'])


def get_simple_post_message(
    text,
    thread=True,
    omnibot_parse=None,
    ephemeral=False
):
    """
    Get a fully formed response for posting a single, simple, text message.

    Args:

        text (str): The text to post in the message.

    Keyword Args:

        thread (bool): Whether or not to post a response in a thread.
        omnibot_parse (list): A list of resources omnibot should parse before
        posting the message.
        ephemeral (bool): Whether to post in-channel or ephemeral.

    Returns:

        An actions dict, with a single chat.postMessage action; example:

        .. code-block:: json

            {
                'actions': [
                    {
                        'action': 'chat.postMessage',
                        'kwargs': {
                            'text': 'example'
                        }
                    }
                ]
            }
    """
    kwargs = {
        'text': text
    }
    if omnibot_parse is not None:
        kwargs['omnibot_parse'] = omnibot_parse
    if not thread:
        kwargs['thread_ts'] = None
    if ephemeral:
        action = 'chat.postEphemeral'
    else:
        action = 'chat.postMessage'
    return {
        'actions': [{
            'action': action,
            'kwargs': kwargs
        }]
    }


def get_simple_response(
    text,
    omnibot_parse=None,
    ephemeral=False,
    replace_original=False
):
    """
    Get a fully formed response for responding back to a slash command or
    interactive component event.

    Args:

        text (str): The text to respond with

    Keyword Args:

        omnibot_parse (list): A list of resources omnibot should parse before
        posting the message.
        ephemeral (bool): Whether to post in-channel or ephemeral.
        replace_original (bool): Whether to replace the original message, or
        respond to it.

    Returns:

        A responses dict, with a single response; example:

        .. code-block:: json

            {
                'responses': [
                    {
                        'response_type': 'ephemeral',
                        'text': 'example'
                    }
                ]
            }
    """
    if ephemeral:
        response_type = 'ephemeral'
    else:
        response_type = 'in_channel'
    if omnibot_parse is None:
        omnibot_parse = {}
    responses = {
        'responses': [
            {
                'response_type': response_type,
                'text': text,
                'omnibot_parse': omnibot_parse,
                'replace_original': replace_original,
            },
        ],
    }
    return responses
