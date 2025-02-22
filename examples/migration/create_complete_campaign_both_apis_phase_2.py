#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This example creates a search campaign with the AdWords and Google Ads APIs.

This code example is the third in a series of code examples that shows how to
create a Search campaign using the AdWords API, and then migrate it to the
Google Ads API one functionality at a time. See other examples in this directory
for code examples in various stages of migration.

In this code example, the functionality to create campaign budget and search
campaign have been migrated to the Google Ads API. The rest of the functionality
- creating ad groups, keywords and expanded text ads are done using the
AdWords API.
"""

import argparse
import collections
import datetime
import sys
import urllib.parse
import uuid

from googleads import adwords

from google.ads.google_ads.client import GoogleAdsClient
from google.ads.google_ads.errors import GoogleAdsException

# Number of ads being added/updated in this code example.
NUMBER_OF_ADS = 5
# The list of keywords being added in this code example.
KEYWORDS_TO_ADD = ['mars cruise', 'space hotel']
PAGE_SIZE = 1000


def create_campaign_budget(client, customer_id):
    """Creates a new campaign budget and returns it.

    Args:
        client: A google.ads.google_ads.client.GoogleAdsClient instance.
        customer_id: (str) Customer ID associated with the account.

    Returns:
        An instance of google.ads.google_ads.v2.types.CampaignBudget for the
            newly created Budget.
    """
    campaign_service = client.get_service('CampaignBudgetService', version='v3')
    operation = client.get_type('CampaignBudgetOperation', version='v3')
    criterion = operation.create
    criterion.name.value = f'Interplanetary Cruise Budget #{uuid.uuid4()}'
    criterion.delivery_method = client.get_type(
                                'BudgetDeliveryMethodEnum',
                                version='v3').STANDARD
    criterion.amount_micros.value = 500000
    response = campaign_service.mutate_campaign_budgets(customer_id,
               [operation])
    campaign_budget_resource_name = response.results[0].resource_name
    new_campaign_budget = get_campaign_budget(client, customer_id,
                          campaign_budget_resource_name)
    print(f'Added budget named {new_campaign_budget.name.value}')
    return new_campaign_budget


def get_campaign_budget(client, customer_id, resource_name):
    """Retrieves a google.ads.google_ads.v2.types.CampaignBudget instance..

    Args:
        client: A google.ads.google_ads.client.GoogleAdsClient instance.
        customer_id: (str) Customer ID associated with the account.
        resource_name: (str) Resource name associated with the newly
            created campaign.
:
        An instance of google.ads.google_ads.v2.types.CampaignBudget for the
            newly created Budget.
    """
    ga_service = client.get_service('GoogleAdsService', version='v3')
    query = f'SELECT campaign_budget.id, campaign_budget.name, campaign_budget.resource_name FROM campaign_budget WHERE campaign_budget.resource_name = "{resource_name}"'
    response = ga_service.search(customer_id, query, PAGE_SIZE)
    return list(response)[0].campaign_budget


def create_campaign(client, customer_id, campaign_budget):
    """Creates a new campaign and returns it.

    Args:
        client: A google.ads.google_ads.client.GoogleAdsClient instance.
        customer_id: (str) Customer ID associated with the account.
        campaign_budget: A google.ads.google_ads.v2.types.CampaignBudget
            message class instance.

    Returns:
        A google.ads.google_ads.v2.types.GoogleAdsClient message class instance.
    """
    operation = client.get_type('CampaignOperation', version='v3')
    campaign = operation.create
    campaign_service = client.get_service('CampaignService', version='v3')
    campaign.name.value = f'Interplanetary Cruise#{uuid.uuid4()}'
    campaign.advertising_channel_type = client.get_type(
                                        'AdvertisingChannelTypeEnum',
                                        version='v3').SEARCH
    # Recommendation: Set the campaign to PAUSED when creating it to stop the
    # ads from immediately serving. Set to ENABLED once you've added
    # targeting and the ads are ready to serve.
    campaign.status = client.get_type('CampaignStatusEnum', version='v3').PAUSED
    campaign.manual_cpc.enhanced_cpc_enabled.value = True
    campaign.campaign_budget.value = campaign_budget.resource_name
    campaign.network_settings.target_google_search.value = True
    campaign.network_settings.target_search_network.value = True
    campaign.network_settings.target_content_network.value = False
    campaign.network_settings.target_partner_search_network.value = False
    campaign.start_date.value =  (datetime.datetime.now() + 
                                  datetime.timedelta(1)).strftime('%Y%m%d')
    campaign.end_date.value = (datetime.datetime.now() + 
                               datetime.timedelta(365)).strftime('%Y%m%d')
    response = campaign_service.mutate_campaigns(customer_id, [operation])
    campaign_resource_name = response.results[0].resource_name
    new_campaign = get_campaign(client, customer_id, campaign_resource_name)
    print(f'Added campaign named {new_campaign.name.value}')
    return new_campaign


def get_campaign(client, customer_id, campaign_resource_name):
    """Retrieves a google.ads.google_ads.v2.types.Campaign instance.

    Args:
        client: A google.ads.google_ads.client.GoogleAdsClient instance.
        customer_id: (str) Customer ID associated with the account.
        campaign_resource_name: (str) Resource name associated with the newly
            created campaign budget.

    Returns:
        A google.ads.google_ads.v2.types.GoogleAdsClient message class instance.
    """
    ga_service = client.get_service('GoogleAdsService', version='v3')
    query = f'SELECT campaign.id, campaign.name, campaign.resource_name FROM campaign WHERE campaign.resource_name = "{campaign_resource_name}" '
    response = ga_service.search(customer_id, query, PAGE_SIZE)
    campaign = list(response)[0].campaign
    return campaign


def create_ad_group(client, campaign_id):
    """Creates a new ad group and returns the newly created ad group id.

    Args:
        client: The ID of the campaign under which to create a new ad group.
        campaign_id: (str) campaign ID to be referenced while creating ad group.

    Returns:
        (str) Ad group ID of the newly created ad group.
    """
    ad_group_service = client.GetService('AdGroupService', 'v201809')
    ad_group = {
        'name': f'Earth to Mars Cruise #{uuid.uuid4()}',
        'campaignId': campaign_id,
        'status': 'ENABLED',
        'biddingStrategyConfiguration': {
            'bids': [
                {
                    # The 'xsi_type' field allows you to specify the xsi:type of the
                    # object being created. It's only necessary when you must
                    # provide an explicit type that the client library can't infer.
                    'xsi_type': 'CpcBid',
                    'bid': {'microAmount': 10000000},
                }
            ]
        },
        'adGroupAdRotationMode': 'OPTIMIZE',
    }

    adgroup_operations = [{
        'operator': 'ADD',
        'operand': ad_group
    }]
    results = ad_group_service.mutate(adgroup_operations)
    created_ad_group = results['value'][0]
    print(
        f"Ad group with ID {created_ad_group['id']} and name {created_ad_group['name']} was created"
    )
    return created_ad_group['id']


def create_text_ads(client, ad_group_id):
    """Creates text ads using the given ad group ID.

    Args:
        client: An instance of the googleads.adwords.AdWordsClient class.
        ad_group_id: (str) Ad group ID to be referenced when creating text ads.
    """
    ad_group_service = client.GetService('AdGroupAdService', 'v201809')
    operations = []
    for _ in range(NUMBER_OF_ADS):
        operation = {
            'xsi_type': 'AdGroupAd',
            'adGroupId': ad_group_id,
            'status': 'PAUSED',
            'ad': {
                'xsi_type': 'ExpandedTextAd',
                'headlinePart1': f'Cruise #{str(uuid.uuid4())[:8]} to Mars',
                'headlinePart2': 'Best Space Cruise Line',
                'headlinePart3': 'For Your Loved Ones',
                'description': 'Buy your tickets now!',
                'description2': 'Discount ends soon',
                'finalUrls': ['http://www.example.com/'],
            },
        }
        adgroup_operations = {
            'operator': 'ADD',
            'operand': operation
         }
        operations.append(adgroup_operations)

    results = ad_group_service.mutate(operations)
    for result in results['value']:
        print(
            f"Expanded text ad with ID {result['ad']['id']} and headline {result['ad']['headlinePart1']}-{result['ad']['headlinePart2']} {result['ad']['headlinePart3']} was created"
        )


def create_keywords(client, ad_group_id, keywords_to_add):
    """Populates keywords on a given ad group ID.

    Args:
        client: An instance of the googleads.adwords.AdWordsClient class.
        ad_group_id: (str) ad group ID to be referenced while creating text ads.
        keywords_to_add: (list) A list of keywords to be added to the ad group.
    """
    ad_group_criterion_service = client.GetService('AdGroupCriterionService',
                                                   'v201809')
    operations = []
    for keyword in keywords_to_add:
        operation = {
            'xsi_type': 'BiddableAdGroupCriterion',
            'adGroupId': ad_group_id,
            'criterion': {
                'xsi_type': 'Keyword',
                'text': keyword,
                'matchType': 'BROAD',
            },
            'userStatus': 'PAUSED',
            'finalUrls': [
                f'http://www.example.com/mars/cruise/?kw={urllib.parse.quote(keyword)}'
            ],
        }
        create_keyword = {
            'operator': 'ADD',
            'operand': operation
        }
        operations.append(create_keyword)

    results = ad_group_criterion_service.mutate(operations)
    for result in results['value']:
        print(
            f"Keyword with ad group ID {result['adGroupId']}, keyword ID {result['criterion']['id']}, text {result['criterion']['text']} and matchtype {result['criterion']['matchType']} was created"
        )


if __name__ == '__main__':
    # Initialize client object.
    # It will read the config file. The default file path is the Home Directory.
    google_ads_client = GoogleAdsClient.load_from_storage()
    adwords_client = adwords.AdWordsClient.LoadFromStorage()

    parser = argparse.ArgumentParser(
        description='Lists all campaigns for specified customer.')
    # The following argument(s) should be provided to run the example.
    parser.add_argument('-c', '--customer_id', type=str,
                        required=True, help='The Google Ads customer ID.')
    args = parser.parse_args()
    budget = create_campaign_budget(google_ads_client, args.customer_id)
    campaign = create_campaign(google_ads_client, args.customer_id, budget)
    ad_group_id = create_ad_group(adwords_client, campaign.id.value)
    create_text_ads(adwords_client, ad_group_id)
    create_keywords(adwords_client, ad_group_id, KEYWORDS_TO_ADD)
