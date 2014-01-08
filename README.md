# Hatch

Hatch is an open source public input tool, targeted at young adults. Use it to expand your outreach and engagement by bringing Twitter conversations into the mix alongside other activities like public meetings. Pose a question or topic, and have a conversation using tweets or directly on your Hatch site. It’s intended to be engaging, visually compelling, and simple to use on mobile devices.

Hatch started as \#VizLou, an experimental new tool for civic engagement, created in partnership with Louisville Metro, with support from Living Cities. [Read more about the project](http://www.livingcities.org/blog/?id=90).

## Is Hatch right for your project?
Hatch is just a tool. You decide how to use it well. Here are the ingredients for a successful Hatch project. Use these questions to decide if Hatch is a good fit for your project. If it is, get started:

* The need: What are the topics you want to gather input on? Pick topics that are suited to gathering and sharing short messages on Twitter, and consider who you want to hear from. What makes this call for input authentic and meaningful to young adults? 
* The convener: Who will lead the conversation, responding to questions? Could be a city hall team, a youth services organization or network of youth services organizations, planning professionals, or a grassroots nonprofit. Who will be watching the hashtag and writing replies?
* The partners: Who will help with outreach and getting the word out? Who are your neighborhood Twitter nodes, to help shape the conversation and engage with young adults? 
* The outreach: Does your project have an outreach plan? How will your intended users find out about your project and your Hatch site? What kind of face-to-face outreach are you planning?  

We’re still evolving these questions, so please give us your feedback on what else you think is important to consider.


## Features

* Collect ideas and start conversations
* Built on the Twitter platform, Hatch will:
  * Import tweets that match your search terms
  * Import any activity that happens on Twitter so won't miss any of the conversation
  * Share activity from the app on Twitter
* Set the topic of conversation; start new topics after older ones have run their course
* Configurable text and images
* Support, comment, or retweet ideas
* Explore user profiles and activity
* Activity notifications

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

    src/manage.py syncdb --all

#### Create a superuser

A superuser will allow you to login to the site admin. Run this command and follow the prompts.

    src/manage.py createsuperuser

#### Configure the app

1. Start the app by running `src/manage.py runserver` in your terminal from your app directory. This runs on port 8000 by default.
2. Go to [http://localhost:8000/admin/](http://localhost:8000/admin/) and login with the credentials you created in the previous step.
3. Click on the [Add link](http://localhost:8000/admin/hatch/appconfig/add/) in the [App configs](http://localhost:8000/admin/hatch/appconfig/) section.
4. Fill in all of the required fields, especially the Twitter app settings. Remember, you can find them with your application settings at [https://dev.twitter.com/](https://dev.twitter.com/). Note that you can change any of these settings later.
5. Click on the [Add link](http://localhost:8000/admin/hatch/category/add/) in the [Categories](http://localhost:8000/admin/hatch/category/) section.
6. Fill in all of the fields. A category describes the prompt you will give your users when they visit the site. Hatch supports multiple categories, but only one at a time.

#### Restart your server

Log out, restart your server (`src/manage.py runserver`), and then visit [your app](http://localhost:8000). Things should be setup correctly if you can login with your Twitter account and submit an idea.


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

Set `CACHE_URL` to the value of `[REDISVENDOR]_URL`

    heroku config:set CACHE_URL=redis://[blahblahblah]/0

**NOTE the** `/0` **at the end. This is the Redis database number and must be included. The actual number is arbitrary, and 0 is a good choice.**

#### Deploy the app

Deploy your code to Heroku now that the environment is all setup.

    git push heroku master

#### Setup and configure the app

Your app is now deployed! Finally, we need to do the final steps which mirror what we did above when setting up our local instance.

#### Setup the database

You don't have any tables yet! Run this to get everything setup for the first time.

    heroku run src/manage.py syncdb --all

#### Create a superuser

A superuser will allow you to login to the site admin. Run this command and follow the prompts.

    heroku run src/manage.py createsuperuser

#### Configure the app

1. Go to `http://[myappname].herokuapp.com/admin/` and login with the credentials you created in the previous step.
2. Click on the Add link in the App configs section.
3. Fill in all of the required fields, especially the Twitter app settings. Remember, you can find them with your application settings at [https://dev.twitter.com/](https://dev.twitter.com/). Note that you can change any of these settings later.
4. Click on the Add link in the Categories section.
5. Fill in all of the fields. A category describes the prompt you will give your users when they visit the site. Hatch supports multiple categories, but only one at a time.

#### Restart your server

Log out, restart your server (`heroku restart`), and then visit your app at `http://[myappname].herokuapp.com`. Things should be setup correctly if you can login with your Twitter account and submit an idea.

#### Keep the user information fresh

On your Heroku dashboard, click the Heroku Scheduler addon. Add the following
scheduled task (job):

    src/manage.py refreshusers

Schedule it to run with a frequency of every 10 minutes.


#### Scale your app

On your Heroku dashboard, go to the Resources section.

* Scale the worker process to 1 dyno. This is what monitors Twitter for new activity.
* Optionally, scale your web process to 2 dynos. This will keep the app from going to sleep.

#### Hatch a conversation

Congratulations! You should now be up and running.
