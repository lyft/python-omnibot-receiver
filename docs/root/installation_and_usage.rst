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

Here is an example of an event payload for an interactive event (in this case, the "Continue Cleanup" button was clicked):

.. code-block:: json

   "event": {
       "actions": [
         {
           "action_id": "continue_cleanup",
           "action_ts": "1709149728.078244",
           "block_id": "oktabot_events",
           "style": "primary",
           "text": {
             "emoji": true,
             "text": "Continue Cleanup",
             "type": "plain_text"
           },
           "type": "button"
         }
       ],
       "bot": {
         "bot_id": "AV3KU59U1",
         "name": "oktabot"
       },
       "callback_id": "oktabot_events",
       "channel": {
         "id": "C06E50DBT45",
         "name": "privategroup"
       },
       "message": {
         "app_id": "AV3KU59U1",
         "blocks": [
           {
             "block_id": "ZocFS",
             "text": {
               "emoji": true,
               "text": ":oktacircle: Okta Cleanup :clean:",
               "type": "plain_text"
             },
             "type": "header"
           },
           {
             "block_id": "eFD0m",
             "fields": [
               {
                 "text": "*Inactive Users:*\n22",
                 "type": "mrkdwn",
                 "verbatim": false
               },
               {
                 "text": "*Suspended Users:*\n5",
                 "type": "mrkdwn",
                 "verbatim": false
               },
               {
                 "text": "*Service Accounts:*\n59",
                 "type": "mrkdwn",
                 "verbatim": false
               },
               {
                 "text": "*Groups with no Apps:*\n48",
                 "type": "mrkdwn",
                 "verbatim": false
               },
               {
                 "text": "*Groups with no Users:*\n15",
                 "type": "mrkdwn",
                 "verbatim": false
               },
               {
                 "text": "*Inactive Apps:*\n18",
                 "type": "mrkdwn",
                 "verbatim": false
               },
               {
                 "text": "*Apps with No Users:*\n2",
                 "type": "mrkdwn",
                 "verbatim": false
               },
               {
                 "text": "*Apps with No Usage:*\n1",
                 "type": "mrkdwn",
                 "verbatim": false
               }
             ],
             "type": "section"
           },
           {
             "block_id": "oktabot_events",
             "elements": [
               {
                 "action_id": "continue_cleanup",
                 "style": "primary",
                 "text": {
                   "emoji": true,
                   "text": "Continue Cleanup",
                   "type": "plain_text"
                 },
                 "type": "button"
               },
               {
                 "action_id": "cancel_cleanup",
                 "style": "danger",
                 "text": {
                   "emoji": true,
                   "text": "Cancel Cleanup",
                   "type": "plain_text"
                 },
                 "type": "button"
               }
             ],
             "type": "actions"
           }
         ],
         "bot_id": "B0101J806MD",
         "channels": [],
         "emails": [],
         "emojis": {
           ":clean:": "clean",
           ":oktacircle:": "oktacircle"
         },
         "parsed_text": ":oktacircle: Okta Cleanup :clean: *Inactive Users:*\n22 *Suspended Users:*\n5 *Service Accounts:*\n59 *Groups with no Apps:*\n48 *Groups with no Users:*\n15 *Inactive Apps:*\n18 *Apps with No Users:*\n2 *Apps with No Usage:*\n1 Continue Cleanup button Cancel Cleanup button",
         "parsed_user": {
           "color": "2b6836",
           "deleted": false,
           "enterprise_user": {
             "enterprise_id": "11111111",
             "enterprise_name": "Lyft Org",
             "id": "12345678",
             "is_admin": false,
             "is_owner": false,
             "is_primary_owner": false,
             "teams": [
               "87654321"
             ]
           },
           "id": "11111111",
           "is_admin": false,
           "is_app_user": false,
           "is_bot": true,
           "is_email_confirmed": false,
           "is_owner": false,
           "is_primary_owner": false,
           "is_restricted": false,
           "is_ultra_restricted": false,
           "name": "oktabot",
           "profile": {
             "always_active": true,
             "api_app_id": "AV3KU59U1",
             "avatar_hash": "ecbc05b8018e",
             "bot_id": "BV0UGFQ02",
             "display_name": "",
             "display_name_normalized": "",
             "first_name": "oktabot",
             "image_1024": "https://avatars.slack-edge.com/2020-04-10/1054481108146_ecbc05b8018e1f0a8d74_1024.jpg",
             "image_192": "https://avatars.slack-edge.com/2020-04-10/1054481108146_ecbc05b8018e1f0a8d74_192.jpg",
             "image_24": "https://avatars.slack-edge.com/2020-04-10/1054481108146_ecbc05b8018e1f0a8d74_24.jpg",
             "image_32": "https://avatars.slack-edge.com/2020-04-10/1054481108146_ecbc05b8018e1f0a8d74_32.jpg",
             "image_48": "https://avatars.slack-edge.com/2020-04-10/1054481108146_ecbc05b8018e1f0a8d74_48.jpg",
             "image_512": "https://avatars.slack-edge.com/2020-04-10/1054481108146_ecbc05b8018e1f0a8d74_512.jpg",
             "image_72": "https://avatars.slack-edge.com/2020-04-10/1054481108146_ecbc05b8018e1f0a8d74_72.jpg",
             "image_original": "https://avatars.slack-edge.com/2020-04-10/1054481108146_ecbc05b8018e1f0a8d74_original.jpg",
             "is_custom_image": true,
             "last_name": "",
             "phone": "",
             "real_name": "oktabot",
             "real_name_normalized": "oktabot",
             "skype": "",
             "status_emoji": "",
             "status_emoji_display_info": [],
             "status_expiration": 0,
             "status_text": "",
             "status_text_canonical": "",
             "team": "T029A67TC",
             "title": ""
           },
           "real_name": "oktabot",
           "team_id": "T029A67TC",
           "tz": "America/Los_Angeles",
           "tz_label": "Pacific Standard Time",
           "tz_offset": -28800,
           "updated": 1621408361,
           "who_can_share_contact_card": "EVERYONE"
         }
       }
   }


See :mod:`omnibot_receiver.router` module documentation for more detailed OmnibotRouter usage.

Responding
^^^^^^^^^^

See :mod:`omnibot_receiver.response` module documentation for response helper functions.
