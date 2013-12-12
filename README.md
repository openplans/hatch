## Hatch

Hatch helps community members share what they love about their communities, and their ideas for the future. Discovering and sharing visions happens over Twitter and directly on the app. City leadership and staff, community leaders, and other adult allies can use the tool to share visions they like, offer comments and help make connections.

Hatch started as \#VizLou, an experimental new tool for civic engagement, created in partnership with Louisville Metro, with support from Living Cities. [Read more about the project](http://www.livingcities.org/blog/?id=90).

## Setup

**Credentials needed:**

* A Google analytics id and domain
* A Twitter account
* A Twitter application
* AWS access key and secret, and S3 bucket(optional)

**Twitter application:**

* On the settings tab
  * Set the callback URL to http://*<your-domain>*/complete/twitter/
  * Check the "Allow this application to be used to Sign in with Twitter" box
* At the bottom of the details tab, click the button to create your access token

**S3 bucket:**

If you want to use S3 for your image storage, do the following:

1. Log in to the AWS console at aws.amazon.com (My Account/Console)
2. Select S3 from "Storage and Content Delivery"
3. Create a bucket named *<your-app>*-media

**Settings:**

Copy the `local_settings.py.template` file to `local_settings.py` and set the following values:

    # AWS Credentials
    AWS_STORAGE_BUCKET_NAME
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

    # Google Analytics logging information
    GOOGLE_ANALYTICS_DOMAIN  # The domain for the app, e.g. 'hatchery.phila.gov'
    GOOGLE_ANALYTICS_ID      # The ID from Google Analytics, e.g. 'UA-12345678-1'
