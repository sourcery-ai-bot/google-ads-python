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
"""This example creates a search campaign with the help of AdWords Api.

This code example is the first in a series of code examples that shows how to
create a Search campaign using the AdWords API, and then migrate it to Google
Ads API one functionality at a time. See other examples in this directory for
code examples in various stages of migration.

This code example represents the initial state, where the AdWords API is used
to create a campaign budget, a Search campaign, ad groups, keywords and expanded
text ads. None of the functionality has yet been migrated to the Google Ads API.
"""


import datetime
import urllib.parse
import uuid

from googleads import adwords

# Number of ads being added/updated in this code example.
NUMBER_OF_ADS = 5
# The list of keywords being added in this code example.
KEYWORDS_TO_ADD = ['mars cruise', 'space hotel']


def create_campaign_budget(client):
    """Creates a new budget and returns the newly created budget ID.

    Args:
        client: An instance of the google.ads.google_ads.client.GoogleAdsClient
        class.

    Returns:
        (str) Budget ID of the newly created budget.
    """
    budget_service = client.GetService('BudgetService', version='v201809')
    budget = {
        'name': f'Interplanetary Cruise Budget #{uuid.uuid4()}',
        'amount': {'microAmount': '50000000'},
        'deliveryMethod': 'STANDARD',
    }
    budget_operations = [{
        'operator': 'ADD',
        'operand': budget
    }]
    # Add budget.
    results = budget_service.mutate(budget_operations)
    created_budget = results['value'][0]
    print(
        f"Budget with ID {created_budget['budgetId']} and name {created_budget['name']} was created"
    )
    return created_budget['budgetId']


def create_campaign(client, budget_id):
    """Creates a new campaign and returns the newly created campaign ID.

    Args:
        client: A google.ads.google_ads.client.GoogleAdsClient instance.
        budget_id: (str) Budget ID to be referenced while creating Campaign.

    Returns:
        (str) Campaign ID of the newly created Campaign.
    """
    campaign_service = client.GetService('CampaignService', version='v201809')
    campaign = {
        'name': f'Interplanetary Cruise #{uuid.uuid4()}',
        'advertisingChannelType': 'SEARCH',
        'status': 'PAUSED',
        'biddingStrategyConfiguration': {
            'biddingStrategyType': 'MANUAL_CPC',
        },
        'startDate': (
            datetime.datetime.now() + datetime.timedelta(1)
        ).strftime('%Y%m%d'),
        'endDate': (
            datetime.datetime.now() + datetime.timedelta(365)
        ).strftime('%Y%m%d'),
        'budget': {'budgetId': budget_id},
        'networkSetting': {
            'targetGoogleSearch': 'true',
            'targetSearchNetwork': 'true',
        },
    }
    campaign_operations = [{
        'operator': 'ADD',
        'operand': campaign
    }]
    results = campaign_service.mutate(campaign_operations)
    created_campaign = results['value'][0]
    print(
        f"CreatedCampign with ID {created_campaign['id']} and name {created_campaign['name']} was created"
    )
    return created_campaign['id']


def create_ad_group(client, campaign_id):
    """Creates a new ad group and returns the new created ad group ID.

    Args:
        client: A google.ads.google_ads.client.GoogleAdsClient instance.
        campaign_id: (str) The ID of the campaign under which to create a new
          ad group.

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
                    # object being created. It's only necessary when you must provide
                    # an explicit type that the client library can't infer.
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
        client: A google.ads.google_ads.client.GoogleAdsClient instance.
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
        client: A google.ads.google_ads.client.GoogleAdsClient instance.
        ad_group_id: (str) Ad group ID to be referenced when creating text ads.
        keywords_to_add: (list) A list of keywords to be added to a given ad
            group.
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
    # Initialize the client object.
    # By default, it will read the config file from the Home Directory.
    adwords_client = adwords.AdWordsClient.LoadFromStorage()
    budget_id = create_campaign_budget(adwords_client)
    campaign_id = create_campaign(adwords_client, budget_id)
    ad_group_id = create_ad_group(adwords_client, campaign_id)
    create_text_ads(adwords_client, ad_group_id)
    create_keywords(adwords_client, ad_group_id, KEYWORDS_TO_ADD)
