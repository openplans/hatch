# Hatch

Hatch helps community members share what they love about their communities, and their ideas for the future. Discovering and sharing visions happens over Twitter and directly on the app. City leadership and staff, community leaders, and other adult allies can use the tool to share visions they like, offer comments and help make connections.

Hatch started as \#VizLou, an experimental new tool for civic engagement, created in partnership with Louisville Metro, with support from Living Cities. [Read more about the project](http://www.livingcities.org/blog/?id=90).

## Setup


### Prerequisites

* A Twitter account
* A Twitter application
* A Google Analytics ID and domain (optional)
* AWS access key and secret, and S3 bucket (optional)

#### Twitter application

* Log into [https://dev.twitter.com/](https://dev.twitter.com/)
* Create a new application
  * Set the callback URL to http://*your-domain*/complete/twitter/
* After creating the application, you can set additional settings
* On the Settings tab
  * Set Application Type to "Read and Write"
  * Check "Allow this application to be used to Sign in with Twitter"
  * Make sure the callback URL to http://*your-domain*/complete/twitter/
* Next, on the Details tab
  * Click the "Create my access token" button (Be sure to do **all** of the previous steps before generating your tokens)

#### S3 bucket

If you want to use S3 for your image storage, do the following:

1. Log in to the AWS Management Console at aws.amazon.com (My Account/Console)
2. Select S3 from "Storage and Content Delivery"
3. Create a bucket named *your-app*-media
4. Get your security credentials, currently found in a menu under your name in the header. You'll need:
  * `AWS_ACCESS_KEY_ID`
  * `AWS_SECRET_ACCESS_KEY`


### Local Setup

#### Settings

Copy the `local_settings.py.template` file to `local_settings.py` and set the following values:

    # AWS Credentials
    AWS_STORAGE_BUCKET_NAME
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

    # Google Analytics logging information
    GOOGLE_ANALYTICS_DOMAIN  # The domain for the app, e.g. 'hatchery.phila.gov'
    GOOGLE_ANALYTICS_ID      # The ID from Google Analytics, e.g. 'UA-12345678-1'

You will need to setup your database settings also to point to your local postgres instance.

#### Setup the database

You don't have any tables yet! Run this to get everything setup for the first time.

    src/manage.py syncdb --migrate

#### Create a superuser

A superuser will allow you to login to the site admin. Run this command and follow the prompts.

    src/manage.py createsuperuser

#### Configure the app

1. Start the app by running `src/manage.py runserver` in your terminal from your app directory. This runs on port 8080 by default.
2. Go to [http://localhost:8080/admin/](http://localhost:8080/admin/) and login with the credentials you created in the previous step.
3. Click on the [Add link](http://localhost:8080/admin/hatch/appconfig/add/) in the [App configs](http://localhost:8080/admin/hatch/appconfig/) section.
4. Fill in all of the required fields, especially the Twitter app settings. Remember, you can find them with your application settings at [https://dev.twitter.com/](https://dev.twitter.com/). Note that you can change any of these settings later.
5. Click on the [Add link](http://localhost:8080/admin/hatch/category/add/) in the [Categories](http://localhost:8080/admin/hatch/category/) section.
6. Fill in all of the fields. A category describes the prompt you will give your users when they visit the site. Hatch supports multiple categories, but only one at a time.
7. Log out, restart your server (`src/manage.py runserver`), and then visit [your app](http://localhost:8080/admin/). Things should be setup correctly if you can login with your Twitter account and submit an idea.


### Deploy to Heroku

#### Create the app

1. Create a Heroku app for your Hatch git repo `heroku apps:create my-app-name`
2. Make sure you add the following Heroku Add-ons
  * Postgresql
  * Rediscloud (or your favorite Redis add-on)
  * Heroku Scheduler

#### Set environment variables

Set the first batch of environment variables on your app. Be sure to replace the dummy values.

    heroku config:set AWS_ACCESS_KEY_ID=[my-aws-access-key-id] \
      AWS_SECRET_ACCESS_KEY=[my-aws-secret-access-key] \
      AWS_STORAGE_BUCKET_NAME=[my-aws-bucket-name] \
      BUILDPACK_URL=https://github.com/ddollar/heroku-buildpack-multi.git \
      GOOGLE_ANALYTICS_DOMAIN=[my-ga-domain] \
      GOOGLE_ANALYTICS_ID=[my-ga-id] \
      IS_HEROKU=True

Next run `heroku config` to see your current environment variables. Heroku names things differently depending on what flavor of add-on you choose, so we need to remap a few of them so that Hatch knows how to read them.

Set `DATABASE_URL` to the value of `HEROKU_POSTGRESQL_[SOME_COLOR]_URL`

    heroku config:set DATABASE_URL=postgres://[blahblahblah]

Set `REDIS_URL` to the value of `[REDISVENDOR]_URL`

    heroku config:set REDIS_URL=redis://[blahblahblah]

#### Deploy the app

Deploy your code to Heroku now that the environment is all setup.

    git push heroku master

#### Keep the user information fresh

On your Heroku dashboard, click the Heroku Scheduler addon. Add the following
scheduled task (job):

    src/manage.py refreshusers

Schedule it to run with a frequency of every 10 minutes.

#### Setup and configure the app

Your app is now deployed! Finally, we need to do the final steps which mirror what we did above when setting up our local instance.

1. [Setup the database](#setup-the-database)
2. [Create a superuser](#create-a-superuser)
3. [Configure the app](#configure-the-app)

#### Hatch a conversation

Congratulations! You should now be up and running.