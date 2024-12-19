# dsd-codered

A plugin for deploying Django projects to CodeRed, using django-simple-deploy.

Quick Start
---

To deploy your project to CodeRed, you'll need to take some steps through the CodeRed web site. But once you set up an initial project there, django-simple-deploy can make all the necessary changes to your project for a successful deployment.

## Prerequisites

Deployment to CodeRed requires the following:

- You must be using Git to track your project.
- You need to be tracking your dependencies with a `requirements.txt` file, or be using Poetry or Pipenv.
- You'll need a [CodeRed account](https://app.codered.cloud/login/), and an [API token](https://www.codered.cloud/docs/cli/quickstart/).
- You need to create a Django project in the CodeRed admin interface:
  - Choose Django, and set the database to Postgres.

## Configuration-only deployment

First, install `dsd-codered` and add `simple_deploy` to `INSTALLED_APPS` in *settings.py*:

```sh
$ pip install dsd-codered cr
# Add "simple_deploy" to INSTALLED_APPS in settings.py.
$ git commit -am "Added simple_deploy to INSTALLED_APPS."
```

When you install `dsd-codered`, it will install `django-simple-deploy` as a dependency. `cr` is CodeRed's [CLI tool](https://www.codered.cloud/docs/cli/); if you already have it installed system-wide, you don't need to install it to your project.

Now run the `deploy` command:

```sh
$ python manage.py deploy
```

This is the `deploy` command from `django-simple-deploy`, which makes all the changes you need to run your project on CodeRed.

At this point, you should review the changes that were made to your project. Running `git status` will show you which files were modified, and which files were created for a successful deployment. If you want to continue with the deployment process, commit these changes. Then set an environment variable with your CodeRed API token, and run the `cr deploy` command:

```sh
$ git add .
$ git commit -m "Configured for deployment to CodeRed."
$ export CR_TOKEN=<api-token>
$ cr deploy <codered-app-name>
```

Here, `<codered-app-name>` is the name you chose when you created a new project in the CodeRed admin interface. The last line of output will show you the URL for your deployed project. You can also find this URL in your CodeRed admin interace.

You can find a record of the deployment process in `simple_deploy_logs`. It contains most of the output you saw when running `deploy`.
