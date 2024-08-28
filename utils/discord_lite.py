import json
import requests
from utils.logger import Logger


def send_discord_webhook(webhook_url, title, content, username=None, as_embed: bool = False):
    """
    Sends a message to a Discord channel using a webhook.

    :param webhook_url: The Discord webhook URL.
    :param title:
    :param content: The message content to send.
    :param username: Optional: The username to display (overrides default).
    :param as_embed:
    """

    # Create the payload for the webhook
    data = {}

    if content and as_embed is not True:
        data["content"] = content

    if username:
        data["username"] = username

    # Create the embed structure
    if as_embed and content:
        embed = {
            "title": f":rotating_light: {title}",
            "description": content,
            "color": 15073402  # Optional: Embed color (hex)
        }

        data["embeds"] = [embed]

    # Send the POST request to the webhook URL
    response = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    # Check the response
    if response.status_code == 204:
        Logger.info("Message sent successfully.")
    else:
        Logger.error(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")


def fetch_recent_messages(bot_token, channel_id, limit=50):
    """
    Fetch recent messages from a channel.

    :param bot_token: Your Discord bot token.
    :param channel_id: The ID of the channel from which to fetch messages.
    :param limit: The number of messages to fetch (default is 50).
    :return: List of recent messages.
    """

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"

    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Return the list of messages
    else:
        Logger.error(f"Failed to fetch messages. Status code: {response.status_code}, Response: {response.text}")
        return []


def publish_message(bot_token, channel_id, message_id):
    """
    Publishes (crossposts) a message in an announcement channel.

    :param bot_token: Your Discord bot token.
    :param channel_id: The ID of the channel where the message was sent.
    :param message_id: The ID of the message to be crossposted.
    """

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}/crosspost"

    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        Logger.info(f"Message {message_id} published (crossposted) successfully.")
    else:
        Logger.error(f"Failed to publish message. Status code: {response.status_code}, Response: {response.text}")


def auto_publish_unpublished_messages(bot_token, channel_id):
    """
    Fetches recent messages from a channel and publishes any unpublished messages.

    :param bot_token: Your Discord bot token.
    :param channel_id: The ID of the channel to check for unpublished messages.
    """

    # Fetch recent messages from the channel
    messages = fetch_recent_messages(bot_token, channel_id)

    if not messages:
        Logger.info("No messages found.")
        return

    # Iterate through the messages and check if they are unpublished
    for message in messages:
        # Check if the message is unpublished
        if message.get("flags") == 0:
            Logger.info(f"Message {message['id']} is unpublished. Publishing, please wait...")
            publish_message(bot_token, channel_id, message["id"])
