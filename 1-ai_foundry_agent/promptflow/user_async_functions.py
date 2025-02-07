# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
import os
import sys
from typing import Any, Callable, Set, Dict, List, Optional
import urllib, urllib.parse
from httpx import AsyncClient, HTTPStatusError, RequestError
import json
import datetime
import re

import aiohttp
from bs4 import BeautifulSoup
from readability import Document

def fetch_current_datetime(format: Optional[str] = None) -> str:
    """
    Get the current time as a JSON string, optionally formatted.

    :param format (Optional[str]): The format in which to return the current time. Defaults to None, which uses a standard format.
    :return: The current time in JSON format.
    :rtype: str
    """
    current_time = datetime.datetime.now()

    # Use the provided format if available, else use a default format
    if format:
        time_format = format
    else:
        time_format = "%Y-%m-%d %H:%M:%S"

    time_json = json.dumps({"current_time": current_time.strftime(time_format)})
    return time_json


async def bing_search(query: str, num_results: int = 3, offset: int = 0) -> str:
    """search Bing for the query and return the search results.

    :param query (str): search query.
    :return: A JSON string 
    :rtype: str
    """
    """Returns the search results of the query provided by pinging the Bing web search API."""
    if not query:
        raise SystemError("query cannot be 'None' or empty.")

    if num_results <= 0:
        raise SystemError("num_results value must be greater than 0.")
    if num_results >= 50:
        raise SystemError("num_results value must be less than 50.")

    if offset < 0:
        raise SystemError("offset must be greater than 0.")


    base_url = ("https://api.bing.microsoft.com/v7.0/search"
    )
    request_url = f"{base_url}?q={urllib.parse.quote_plus(query)}&count={num_results}&offset={offset}" 

    headers = {"Ocp-Apim-Subscription-Key": os.environ.get("BING_SEARCH_KEY")}

    try:
        async with AsyncClient(timeout=5) as client:
            response = await client.get(request_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            pages = data.get("webPages", {}).get("value")
            if pages:
                formatted_pages = []
                for page in pages:
                    date_published = page.get('datePublished', 'N/A')
                    if date_published != 'N/A':
                        try:
                            date_published = date_published[:10] #datetime.datetime.strptime(date_published, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
                        except ValueError:
                            date_published = 'N/A'
                    formatted_pages.append(f"{page['snippet']} (URL: {page['url']}, Date Published: {date_published})")
                return json.dumps({'q':query, 'r': formatted_pages})
            return ''
    except HTTPStatusError as ex:
        raise SystemError("Failed to get search results.") from ex
    except RequestError as ex:
        raise SystemError("A client error occurred while getting search results.") from ex
    except Exception as ex:
        raise SystemError("An unexpected error occurred while getting search results.") from ex


def is_probably_readable(soup: BeautifulSoup, min_score: int = 100) -> bool:
    # Implement a function to check if the document is probably readable
    # This is a placeholder implementation
    return True

async def readable_text(params: Dict[str, Any]) -> Optional[str]:
    html = params['html']
    url = params['url']
    settings = params['settings']
    options = params.get('options', {})

    # Parse the HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Check if the document is probably readable
    if options.get('fallback_to_none') and not is_probably_readable(soup):
        return html

    # Use readability to parse the document
    doc = Document(html)
    parsed = doc.summary()
    parsed_title = doc.title()

    # Create a new BeautifulSoup object for the parsed content
    readability_soup = BeautifulSoup(parsed, 'html.parser')

    # Insert the title at the beginning of the content
    if parsed_title:
        title_element = readability_soup.new_tag('h1')
        title_element.string = parsed_title
        readability_soup.insert(0, title_element)

    return str(readability_soup)

async def process_html(html: str, url: str, settings: dict, soup: BeautifulSoup) -> str:
        body = soup.body
        if 'remove_elements_css_selector' in settings:
            for element in body.select(settings['remove_elements_css_selector']):
                element.decompose()
        
        simplified_body = body.decode_contents().strip()
        #simplified_body = re.sub(r'class="[^"]*"', '', simplified_body)


        if isinstance(simplified_body, str):
            simplified = f"""<html lang="">
            <head>
                <title>
                    {soup.title.string if soup.title else ''}
                </title>
            </head>
            <body>
                {simplified_body}
            </body>
        </html>"""
        else:
            simplified = html or ''

        ret = None
        if settings.get('html_transformer') == 'readableText':
            try:
                ret = await readable_text({'html': simplified, 'url': url, 'settings': settings, 'options': {'fallback_to_none': False}})
            except Exception as error:
                print(f"Processing of HTML failed with error: {error}")

        return ret or simplified
    
async def get_webpage(url: str) -> str:
    """Sends an HTTP GET request to the specified URI and returns the response body as a string.

    :param url (str): webpage url.
    :return: A string containing webpage content. 
    :rtype: str
    """
    """Returns the content of the webpage at the specified URL."""
    if not url:
        raise SystemError("url cannot be `None` or empty")

    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, raise_for_status=True) as response:
            response_text = await response.text()
            result = await process_html(response_text,  url, {'html_transformer': 'readableText','readableTextCharThreshold': 500}, BeautifulSoup(response_text, 'html.parser'))
            return result

# Statically defined user functions for fast reference with send_email as async but the rest as sync
user_async_function_tools: Set[Callable[..., Any]] = {
    fetch_current_datetime,
    bing_search,
    get_webpage,
}
