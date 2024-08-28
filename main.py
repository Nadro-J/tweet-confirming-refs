import os
import time
import json
from utils.twitter import *
from utils.discord_lite import *
from dotenv import load_dotenv
from utils.logger import Logger
from utils.datamanager import DataManager
from substrateinterface import SubstrateInterface
from websocket._exceptions import WebSocketException
from utils.gov_platforms import fetch_referendum_data


class ConfirmingReferendums:
    def __init__(self, url=None):
        try:
            if url is None or url == '':
                Logger.error('No URL provided. Please provide a URL to connect.')
                raise ValueError('No URL provided. Please provide a URL in the .env config to connect.')

            self.substrate = SubstrateInterface(url=url, auto_reconnect=True, ws_options={'close_timeout': 15, 'open_timeout': 15})
            Logger.info(f"Successfully connected to {url}")

        except WebSocketException as error:
            Logger.error(f"Unable to connect: {error.args}")
            raise WebSocketException(f"Unable to connect: {error.args}")

    def get_average_block_time(self, num_blocks=255):
        latest_block_num = self.substrate.get_block_number(block_hash=self.substrate.block_hash)
        first_block_num = latest_block_num - num_blocks

        first_timestamp = self.substrate.query(
            module='Timestamp',
            storage_function='Now',
            block_hash=self.substrate.get_block_hash(first_block_num)
        ).value

        last_timestamp = self.substrate.query(
            module='Timestamp',
            storage_function='Now',
            block_hash=self.substrate.get_block_hash(latest_block_num)
        ).value

        return (last_timestamp - first_timestamp) / (num_blocks * 1000)

    def time_until_block(self, target_block: int) -> tuple[int, int, int]:
        """
        Calculate the estimated time in minutes until the specified target block is reached on the Kusama network.

        Args:
            target_block (int): The target block number for which the remaining time needs to be calculated.

        Returns:
            int: The estimated time remaining in minutes until the target block is reached. If the target block has
            already been reached, the function will return None.

        Raises:
            Exception: If any error occurs while trying to calculate the time remaining until the target block.
        """
        current_block = self.substrate.get_block_number(block_hash=self.substrate.block_hash)

        # Calculate the difference in blocks
        block_difference = target_block - current_block

        # Get the average block time (6 seconds for Kusama)
        avg_block_time = self.get_average_block_time()

        # Calculate the remaining time in seconds
        remaining_time = block_difference * avg_block_time

        # Convert seconds to days, hours, and minutes
        days = remaining_time // 86400
        remaining_time %= 86400
        hours = remaining_time // 3600
        remaining_time %= 3600
        minutes = remaining_time // 60

        return int(days), int(hours), int(minutes)

    def referendumInfoFor(self):
        referendum_data = {}
        cache_confirmations = {}
        referendums = self.substrate.query_map(module='Referenda',
                                               storage_function='ReferendumInfoFor',
                                               params=[])

        for index, info in referendums:
            if 'Ongoing' in info:
                referendum_data.update({index.value: info.value})

        sort = json.dumps(referendum_data, indent=4, sort_keys=True)
        data = json.loads(sort)
        cached_conf_refs = DataManager.load_data_from_cache(filename='data/confirmations.json').keys()

        origin_mapping = {
            "SmallTipper": {
                "dot_spend": 250,
                "multiplier": 1
            },
            "BigTipper": {
                "dot_spend": 1000,
                "multiplier": 1
            },
            "SmallSpender": {
                "dot_spend": 10000,
                "multiplier": 2
            },
            "MediumSpender": {
                "dot_spend": 100000,
                "multiplier": 3
            },
            "BigSpender": {
                "dot_spend": 1000000,
                "multiplier": 4
            }
        }

        for index, info in data.items():
            deciding = info['Ongoing'].get('deciding', None)
            if deciding is not None:
                confirming = deciding.get('confirming', None)
                if confirming is not None:
                    confirming = self.time_until_block(confirming)
                    origin = info['Ongoing'].get('origin', None).get('Origins', None)
                    days, hours, minutes = confirming[0], confirming[1], confirming[2]

                    Logger.info(f"{index} is Confirming in {days}d:{hours}hrs:{minutes}mins")

                    cache_confirmations.update({
                        index: {"days": days,
                                "hours": hours,
                                "minutes": minutes}
                    })

                    if index not in cached_conf_refs or confirming[1] <= 2 and confirming[0] == 0:
                        Logger.info("Preparing tweet")

                        final_3hr_confirmation = None
                        if confirming[1] <= 6 and confirming[0] == 0:
                            final_3hr_confirmation = '🔥'
                        gov_platform_data = fetch_referendum_data(referendum_id=index, network=os.environ['CHAIN'])
                        twitter = TwitterAuth(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'],
                                              os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])

                        final_3hr_confirmation = final_3hr_confirmation if final_3hr_confirmation is not None else ""
                        tweet = (f'{gov_platform_data["title"]} #{index} is confirming in {days}d {hours}hrs {minutes}mins\n\n'
                                 f'https://polkadot.subsquare.io/referenda/{index}'
                                 f'\n#Polkadot #Governance {final_3hr_confirmation}')

                        send_discord_webhook(os.environ['WEBHOOK'], title="Confirming Referendum Alert", content=tweet, username="Confirming Referendum", as_embed=True)

                        twitter.post_tweet(text=tweet)
                        Logger.info(f"Tweet executed for ref {index}! sleeping for 5 seconds...")
                        time.sleep(5)

        auto_publish_unpublished_messages(os.environ['PUBLISHING_BOT_TOKEN'], os.environ['ANNOUNCEMENT_CHANNEL'])
        DataManager.save_data_to_cache(filename='./data/confirmations.json', data=cache_confirmations)
        return cache_confirmations


if __name__ == "__main__":
    Logger.configure(log_level=3, filename_prefix='ConfirmingRefs')
    Logger.info("Initializing")

    load_dotenv()

    polkadot = ConfirmingReferendums(url=os.environ['SUBSTRATE_WSS'])
    polkadot.referendumInfoFor()
