import time
import json
import cloudscraper
from functools import lru_cache
from random import choice
from urllib.parse import unquote

import settings


class RemoteProvider:
    def __init__(self, targets=None):
        self.targets = [unquote(target) for target in targets] if targets else None
        self._proxies = []
        self.sites = []
        self.scraper = cloudscraper.create_scraper(browser=settings.BROWSER, )

    def _scrap_json_from_site(self, link):
        host = choice(link)
        content = self.scraper.get(host).content
        if content:
            try:
                data = json.loads(content)
                return data
            except json.decoder.JSONDecodeError:
                raise Exception('Host {} has invalid format'.format(host))
            except Exception:
                raise Exception('Unexpected error. Host {}'.format(host))
        else:
            raise Exception('Unexpected error. Host {}'.format(host))

    def _get_ttl_hash(seconds=settings.TARGET_UPDATE_RATE):
        """Return the same value within `seconds` time period"""
        return round(time.time() / seconds)

    @lru_cache()
    def get_target_sites(self, ttl_hash=_get_ttl_hash()):
        del ttl_hash
        if self.targets:
            self.sites = self.targets
        else:
            try:
                with open("sites.txt","r") as sites_file:

                    self.sites = []
                    for site in sites_file.readlines():
                        if site == " ":
                            continue
                        # if 'attack' not in site or ('attack' in site and not site['attack'] == 0):
                        site = site.strip()
                        if not site.startswith('http'):
                            site = "https://" + site
                        self.sites.append(unquote(site))
            except Exception as e:
                raise e

        return self.sites

    @lru_cache()
    def get_proxies(self, ttl_hash=_get_ttl_hash()):
        del ttl_hash
        try:
            data = self._scrap_json_from_site(settings.PROXIES_HOSTS)
            self._proxies = data
        except Exception as e:
            raise e

        return self._proxies
