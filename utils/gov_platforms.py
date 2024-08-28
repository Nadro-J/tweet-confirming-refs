import requests
from utils.logger import Logger


def fetch_referendum_data(referendum_id: int, network: str):
    """
    Fetches referendum data from a set of URLs using a given referendum ID and network name.

    The function makes HTTP GET requests to each URL in the list. If a response is successful
    and the JSON response contains a non-empty 'title', the function will immediately return
    that response without checking the remaining URLs. If none of the responses are successful,
    the function returns a default response indicating that the referendum details could not
    be retrieved.

    Parameters:
    referendum_id (int): The ID of the referendum to fetch data for.
    network (str): The name of the network where the referendum is held. This is used to
                   construct the URLs and to set the 'x-network' header in the HTTP requests.

    Returns:
    dict: A dictionary containing the referendum data. This dictionary includes a 'title' key,
          a 'content' key, and a 'successful_url' key. If no successful response is received
          from any of the URLs, the 'title' will be 'None', the 'content' will be a message
          indicating that the details could not be retrieved, and the 'successful_url' will be
          None. Otherwise, the returned dictionary will be the successful JSON response from
          one of the URLs, with a 'successful_url' key added to indicate which URL the
          response came from.
    """
    urls = [
        f"https://api.polkassembly.io/api/v1/posts/on-chain-post?postId={referendum_id}&proposalType=referendums_v2",
        f"https://{network}.subsquare.io/api/gov2/referendums/{referendum_id}",
    ]

    headers = {"x-network": network}
    successful_response = None
    successful_url = None

    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            json_response = response.json()

            # Add 'title' key if it doesn't exist
            if "title" not in json_response.keys():
                json_response["title"] = "None"

            # Check if 'title' is not None or empty string
            if json_response["title"] not in {None, "None", ""}:
                successful_response = json_response
                successful_url = url
                # Once a successful response is found, no need to continue checking other URLs
                break

        except requests.exceptions.HTTPError as http_error:
            Logger.error(f"HTTP exception occurred while accessing {url}: {http_error}")

    if successful_response is None:
        return {
            "title": "None",
            "content": "Unable to retrieve details from both sources",
            "successful_url": None
        }
    else:
        successful_response["successful_url"] = successful_url
        return successful_response
