#!/usr/bin/env python
# Copyright 2018 Google LLC
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
"""Demonstrates how to create a shared list of negative broad match keywords.

Note that the keywords will be attached to the specified campaign.
"""


import argparse
import sys
import uuid

import google.ads.google_ads.client


def main(client, customer_id, campaign_id):
    campaign_service = client.get_service('CampaignService', version='v3')
    shared_set_service = client.get_service('SharedSetService', version='v3')
    shared_criterion_service = client.get_service('SharedCriterionService',
                                                  version='v3')
    campaign_shared_set_service = client.get_service('CampaignSharedSetService',
                                                     version='v3')

    # Create shared negative keyword set.
    shared_set_operation = client.get_type('SharedSetOperation', version='v3')
    shared_set = shared_set_operation.create
    shared_set.name.value = f'API Negative keyword list - {uuid.uuid4()}'
    shared_set.type = client.get_type('SharedSetTypeEnum',
                                      version='v3').NEGATIVE_KEYWORDS

    try:
        shared_set_resource_name = shared_set_service.mutate_shared_sets(
            customer_id, [shared_set_operation]).results[0].resource_name
    except google.ads.google_ads.errors.GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status "{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print('\tError with message "%s".' % error.message)
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print('\t\tOn field: %s' % field_path_element.field_name)
        sys.exit(1)

    print(f'Created shared set "{shared_set_resource_name}".')

    shared_criteria_operations = []
    keywords = ['mars cruise', 'mars hotels']
    for keyword in keywords:
        shared_criterion_operation = client.get_type('SharedCriterionOperation',
                                                     version='v3')
        shared_criterion = shared_criterion_operation.create
        keyword_info = shared_criterion.keyword
        keyword_info.text.value = keyword
        keyword_info.match_type = client.get_type('KeywordMatchTypeEnum',
                                                  version='v3').BROAD
        shared_criterion.shared_set.value = shared_set_resource_name
        shared_criteria_operations.append(shared_criterion_operation)

    try:
        response = shared_criterion_service.mutate_shared_criteria(
            customer_id, shared_criteria_operations)
    except google.ads.google_ads.errors.GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status "{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print('\tError with message "%s".' % error.message)
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print('\t\tOn field: %s' % field_path_element.field_name)
        sys.exit(1)

    for shared_criterion in response.results:
        print(f'Created shared criterion "{shared_criterion.resource_name}".')

    campaign_set_operation = client.get_type('CampaignSharedSetOperation',
                                             version='v3')
    campaign_set = campaign_set_operation.create
    campaign_set.campaign.value = campaign_service.campaign_path(
        customer_id, campaign_id)
    campaign_set.shared_set.value = shared_set_resource_name

    try:
        campaign_shared_set_resource_name = (
            campaign_shared_set_service.mutate_campaign_shared_sets(
                customer_id, [campaign_set_operation]).results[0].resource_name)
    except google.ads.google_ads.errors.GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status "{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print('\tError with message "%s".' % error.message)
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print('\t\tOn field: %s' % field_path_element.field_name)
        sys.exit(1)

    print(f'Created campaign shared set "{campaign_shared_set_resource_name}".')


if __name__ == '__main__':
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    google_ads_client = (google.ads.google_ads.client.GoogleAdsClient
                         .load_from_storage())

    parser = argparse.ArgumentParser(
        description=('Adds a list of negative broad match keywords to the '
                     'provided campaign, for the specified customer.'))
    # The following argument(s) should be provided to run the example.
    parser.add_argument('-c', '--customer_id', type=str,
                        required=True, help='The Google Ads customer ID.')
    parser.add_argument('-i', '--campaign_id', type=str,
                        required=True, help='The campaign ID.')
    args = parser.parse_args()

    main(google_ads_client, args.customer_id, args.campaign_id)
