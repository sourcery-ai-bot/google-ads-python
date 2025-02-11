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
"""This example generates forecast metrics for a keyword plan.

To create a keyword plan, run the add_keyword_plan.py example.
"""


import argparse
import sys

from google.ads.google_ads.client import GoogleAdsClient
from google.ads.google_ads.errors import GoogleAdsException


def main(client, customer_id, keyword_plan_id):
    keyword_plan_service = client.get_service('KeywordPlanService')
    resource_name = keyword_plan_service.keyword_plan_path(customer_id,
                                                           keyword_plan_id)

    try:
        response = keyword_plan_service.generate_forecast_metrics(resource_name)
    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status "%s" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f'\t\tOn field: {field_path_element.field_name}')
        sys.exit(1)

    for i, forecast in enumerate(response.keyword_forecasts):
        print(f'#{i + 1} Keyword ID: {forecast.keyword_plan_ad_group_keyword.value}')

        metrics = forecast.keyword_forecast

        click_val = metrics.clicks.value
        clicks = '{:.2f}'.format(click_val) if click_val else 'unspecified'
        print(f'Estimated daily clicks: {clicks}')

        imp_val = metrics.impressions.value
        impressions = '{:.2f}'.format(imp_val) if imp_val else 'unspecified'
        print(f'Estimated daily impressions: {impressions}')

        cpc_val = metrics.average_cpc.value
        cpc = '{:.2f}'.format(cpc_val) if cpc_val else 'unspecified'
        print(f'Estimated average cpc: {cpc}\n')


if __name__ == '__main__':
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    google_ads_client = GoogleAdsClient.load_from_storage()

    parser = argparse.ArgumentParser(
        description='Generates forecast metrics for a keyword plan.')
    # The following argument(s) should be provided to run the example.
    parser.add_argument('-c', '--customer_id', type=str,
                        required=True, help='The Google Ads customer ID.')
    parser.add_argument('-k', '--keyword_plan_id', type=str,
                        required=True, help='A Keyword Plan ID.')
    args = parser.parse_args()

    main(google_ads_client, args.customer_id, args.keyword_plan_id)
