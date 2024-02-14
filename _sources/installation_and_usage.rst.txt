Installation and Usage
======================

Installation
------------

.. code-block:: bash

   pip install omnibot-receiver

Usage
-----

Routing
^^^^^^^

Here's a really basic example, that'll route message events, and interactive commands, when received at endpoint ``/api/v1/bot``:

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


    @message_router.route(
        'ping',
        match_type='command',
        help='Responds to pings with pongs'
    )
    def ping(message):
        ret = {'actions': []}
        ret['actions'].append({
            'action': 'chat.postMessage',
            'kwargs': {'text': 'pong'}
        })
        return ret

   @interactive_router.route('ping_callback')
   def ping(event):
       ret = {'actions': []}
       ret['actions'].append({
           'action': 'chat.postMessage',
           'kwargs': {'text': 'pong'}
       })
       return ret

    @flask_app.route('/api/v1/bot', methods=['POST'])
    def pingbot_route():
        message = request.get_json()
        ret = router.handle_event(message)
        return jsonify(ret)

The above example will respond with ``pong``, when a user sends ``@pingbot ping``, or when an user interacts with an interactive component, which sends the ``ping_callback`` event.

See :mod:`omnibot_receiver.router` module documentation for more detailed OmnibotRouter usage.

Responding
^^^^^^^^^^

See :mod:`omnibot_receiver.response` module documentation for response helper functions.
