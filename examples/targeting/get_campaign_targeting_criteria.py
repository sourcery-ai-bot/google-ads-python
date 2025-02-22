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
"""This example illustrates how to get campaign criteria, or negative keywords.
"""


import argparse
import sys

import google.ads.google_ads.client


_DEFAULT_PAGE_SIZE = 1000


def main(client, customer_id, campaign_id, page_size):
    ga_service = client.get_service('GoogleAdsService', version='v3')

    query = ('SELECT campaign.id, campaign_criterion.campaign, '
             'campaign_criterion.criterion_id, campaign_criterion.negative, '
             'campaign_criterion.type, campaign_criterion.keyword.text, '
             'campaign_criterion.keyword.match_type '
             'FROM campaign_criterion '
             'WHERE campaign.id = %s') % campaign_id

    results = ga_service.search(customer_id, query=query, page_size=page_size)

    try:
        for row in results:
            criterion = row.campaign_criterion
            print(
                f'Campaign criterion with ID "{criterion.criterion_id.value}" was retrieved:'
            )

            if criterion.type == client.get_type('CriterionTypeEnum',
                                                 version='v3').KEYWORD:
                print('\t%sKeyword with text "%s" and match type %s.'
                      % ('' if criterion.negative.value else 'Negative',
                         criterion.keyword.text.value,
                         criterion.keyword.match_type))
            else:
                print('Not a keyword!')
    except google.ads.google_ads.errors.GoogleAdsException as ex:
        print('Request with ID "%s" failed with status "%s" and includes the '
              'following errors:' % (ex.request_id, ex.error.code().name))
        for error in ex.failure.errors:
            print('\tError with message "%s".' % error.message)
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print('\t\tOn field: %s' % field_path_element.field_name)
        sys.exit(1)


if __name__ == '__main__':
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    google_ads_client = (google.ads.google_ads.client.GoogleAdsClient
                         .load_from_storage())

    parser = argparse.ArgumentParser(
        description=('List campaign criteria, or negative keywords, for a '
                     'given campaign.'))
    # The following argument(s) should be provided to run the example.
    parser.add_argument('-c', '--customer_id', type=str,
                        required=True, help='The Google Ads customer ID.')
    parser.add_argument('-i', '--campaign_id', type=str,
                        required=True, help='The campaign ID.')
    args = parser.parse_args()

    main(google_ads_client, args.customer_id, args.campaign_id,
         _DEFAULT_PAGE_SIZE)
