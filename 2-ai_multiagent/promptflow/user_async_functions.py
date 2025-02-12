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
    get_webpage,
}
