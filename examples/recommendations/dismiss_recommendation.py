#!/usr/bin/env python
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
"""This example dismisses a given recommendation.

To retrieve recommendations for text ads, run get_text_ad_recommendations.py.
"""


import argparse
import sys

import google.ads.google_ads.client


def main(client, customer_id, recommendation_id):
    recommendation_service = client.get_service('RecommendationService')

    dismiss_recommendation_request = client.get_type(
        'DismissRecommendationRequest')

    dismiss_recommendation_operation = (dismiss_recommendation_request.
                                        DismissRecommendationOperation())

    dismiss_recommendation_operation.resource_name = (
        recommendation_service.recommendation_path(
            customer_id, recommendation_id))

    try:
        dismissal_response = recommendation_service.dismiss_recommendation(
            customer_id,
            [dismiss_recommendation_operation])
    except google.ads.google_ads.errors.GoogleAdsException as ex:
        print('Request with ID "%s" failed with status "%s" and includes the '
              'following errors:' % (ex.request_id, ex.error.code().name))
        for error in ex.failure.errors:
            print('\tError with message "%s".' % error.message)
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print('\t\tOn field: %s' % field_path_element.field_name)
        sys.exit(1)

    print(
        f'Dismissed recommendation with resource name: "{dismissal_response.results[0].resource_name}".'
    )


if __name__ == '__main__':
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    google_ads_client = (google.ads.google_ads.client.GoogleAdsClient
                         .load_from_storage())

    parser = argparse.ArgumentParser(
        description=('Dismisses a recommendation with the given ID.'))
    # The following argument(s) should be provided to run the example.
    parser.add_argument('-c', '--customer_id', type=str,
                        required=True, help='The Google Ads customer ID.')
    parser.add_argument('-r', '--recommendation_id', type=str,
                        required=True, help='The recommendation ID.')
    args = parser.parse_args()

    main(google_ads_client, args.customer_id, args.recommendation_id)
