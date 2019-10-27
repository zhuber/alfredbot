import os
import logging
import asyncio
import random
import ssl as ssl_lib

import certifi
import slack

from alfredbot import AlfredBot
from attrdict import AttrDict

# Keep track of pending PR notices.
pr_notices = {}


# Notifty a random developer that they are assigned to review a PR
async def notify_developer(web_client: slack.WebClient, user_id: str, channel: str, link: str):
    # Notify a random developer that they are assigned to review the PR.
    alfredbot = AlfredBot(channel)

    message = alfredbot.get_direct_message_payload(user_id, link)

    # Post the assignment message in the current slack channel.
    response = await web_client.chat_postMessage(**message)

    # Keep track of the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an assigned PR review.
    alfredbot.timestamp = response["ts"]

    # Store the message so we can update it later
    if channel not in pr_notices:
        pr_notices[channel] = {}
    pr_notices[channel][user_id] = alfredbot


# Reaction listener
# Respond to users emoji reactions
@slack.RTMClient.run_on(event="reaction_added")
async def update_emoji(**payload):
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data["item"]["channel"]
    user_id = data["user"]
    reaction = data["reaction"]
    # Only look for "completed" reactions for existing assignment messages.
    if (reaction != 'white_check_mark' and reaction != 'checkered_flag') or (channel_id not in pr_notices or user_id not in pr_notices[channel_id]):
        return False
    
    # Get the original PR assignment message.
    alfredbot = pr_notices[channel_id][user_id]

    # Mark the assigned PR as completed.
    alfredbot.pr_completed = True
    print('alfred', alfredbot)
    # Update the assignment message.
    message = alfredbot.get_direct_message_payload(user_id, alfredbot.link)

    # Close the pending assignment message in slack.
    updated_message = await web_client.chat_update(**message)

    # Update the timestamp saved on the assignment message.
    alfredbot.timestamp = updated_message["ts"]


# Message listener
# Respond to opened pull requests.
@slack.RTMClient.run_on(event="message")
async def message(**payload):
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data.get("channel")
    attachments = data.get("attachments")
    if (attachments):
        for attachment in attachments :
            attributes = AttrDict(attachment)
            if (attributes.pretext and (attributes.pretext.find('Pull request opened') != -1 or attributes.pretext.find('Pull request reopened') != -1)) :
                response = await web_client.conversations_members(channel=channel_id)
                users = response.get('members')
                user = random.choice(users)
                return await notify_developer(web_client, user, channel_id, attributes.title_link)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_token = os.environ["ALFRED_BOT_TOKEN"]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    rtm_client = slack.RTMClient(
        token=slack_token, ssl=ssl_context, run_async=True, loop=loop
    )
    loop.run_until_complete(rtm_client.start())