import os
import logging
import asyncio
import random
import ssl as ssl_lib

import certifi
import slack

from slacksybot import SlacksyBot
from attrdict import AttrDict

# Keep track of pending PR notices.
pr_notices = {}
bots = {}
user_map = {}

def filterMembers(member, user_name):
    return (not member in bots and (not user_name in user_map or user_map[user_name] != member))

# Notify a random developer that they are assigned to review a PR
async def notify_developer(web_client: slack.WebClient, user_id: str, channel: str, user_name: str, link: str):
    # Notify a random developer that they are assigned to review the PR.
    slacksybot = SlacksyBot(channel)

    message = slacksybot.get_direct_message_payload(user_id, user_name, link)

    # Post the assignment message in the current slack channel.
    response = await web_client.chat_postMessage(**message)

    # Keep track of the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an assigned PR review.
    slacksybot.timestamp = response["ts"]

    # Store the message so we can update it later
    if channel not in pr_notices:
        pr_notices[channel] = {}
    pr_notices[channel][slacksybot.timestamp] = slacksybot


# Reaction listener
# Respond to users emoji reactions
@slack.RTMClient.run_on(event="reaction_added")
async def update_emoji(**payload):
    data = payload["data"]
    web_client = payload["web_client"]
    channel_id = data["item"]["channel"]
    timestamp = data["item"]["ts"]
    user_id = data["user"]
    reaction = data["reaction"]

    # Only look for "completed" reactions for existing assignment messages.
    if (channel_id not in pr_notices or timestamp not in pr_notices[channel_id]):
        return False

    # Get the original PR assignment message.
    slacksybot = pr_notices[channel_id][timestamp]

    # Mark the current reviewer as a bot, so we can ignore that user id later.
    if (reaction == 'robot_face'):
        # Parse the bot's user id based on the message.
        slacksybot.bad_assignment = True
        # Unset the pending PR.
        pr_notices[channel_id][timestamp]
        bots[slacksybot.user_id] = True
        slacksybot.user_name = 'now on'

    # Keep track of the current user name and user id to avoid bad assignments later.
    if (reaction == 'man-gesturing-no' or reaction == 'woman-gesturing-no'):
        # Parse the bot's user id based on the message.
        slacksybot.bad_assignment = True
        # Unset the pending PR.
        pr_notices[channel_id][timestamp]
        user_map[slacksybot.user_name] = slacksybot.user_id

    # Ignore any other non-relevant emoji reactions.
    if (reaction == 'white_check_mark' or reaction == 'checkered_flag'):
        # Mark the assigned PR as completed.
        slacksybot.pr_completed = True
        # Unset the pending PR.
        pr_notices[channel_id][timestamp]

    if (slacksybot.pr_completed or slacksybot.bad_assignment):
        # Update the assignment message.
        message = slacksybot.get_direct_message_payload(slacksybot.user_id, slacksybot.user_name, slacksybot.link)
        # Close the pending assignment message in slack.
        updated_message = await web_client.chat_update(**message)
        # Update the timestamp saved on the assignment message.
        slacksybot.timestamp = updated_message["ts"]
        pr_notices[channel_id][slacksybot.timestamp]


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
                # Get the github username.
                message_info = attributes.pretext.split(' by ')
                user_name = message_info[1]
                # Get all members in the slack room.
                response = await web_client.conversations_members(channel=channel_id)
                members = response.get('members')
                # Filter out any bots or matching user ids.
                users = list(filter(lambda x: filterMembers(x, user_name), members))
                if (users):
                    user = random.choice(users)
                    return await notify_developer(web_client, user, channel_id, user_name, attributes.title_link)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_token = os.environ["SLACKSY_BOT_TOKEN"]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    rtm_client = slack.RTMClient(
        token=slack_token, ssl=ssl_context, run_async=True, loop=loop
    )
    loop.run_until_complete(rtm_client.start())