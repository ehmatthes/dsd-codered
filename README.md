# dsd-codered

A plugin for deploying Django projects to CodeRed, using django-simple-deploy.

Quick Start
---

Overview

To deploy your project to CodeRed, you'll need to take some steps through the CodeRed web site. But once you set up an initial project there, django-simple-deploy can make all the necessary changes to your project for a successful deployment.

## Prerequisites

Deployment to CodeRed requires three things:

- You must be using Git to track your project.
- You need to be tracking your dependencies with a `requirements.txt` file, or be using Poetry or Pipenv.
- The [CodeRed](https://www.codered.cloud/docs/cli/install/) must be installed on your system.
  - You'll also need a [CodeRed account](https://app.codered.cloud/login/), and an [API token](https://www.codered.cloud/docs/cli/quickstart/).

## Deployment

- Create a Django project on CodeRed.
  - Use the same name for the CodeRed project as you used when running `startproject`.