import os

from fabric.api import env, local, lcd
from pydiploy.decorators import do_verbose


@do_verbose
def env_setup():
    local_repo = local("pwd", capture=True)
    distant_repo = local("git config --get remote.origin.url", capture=True)
    temp_dir = local("mktemp -d", capture=True)
    working_dir = os.path.join(temp_dir, "git-clone")
    project_version = ""

    print(local_repo)
    print(distant_repo)
    print(temp_dir)
    print(working_dir)

    # First we git clone the local repo in the local tmp dir
    with lcd(temp_dir):
        print("Cloning local repo in {}".format(local("pwd", capture=True)))
        local("git clone {} {}".format(local_repo, working_dir))
    with lcd(working_dir):
        # As a result of the local git clone, the origin of the cloned repo is the local repo
        # So we reset it to be the distant repo
        print("Setting origin in the temp repo to be {}".format(distant_repo))
        local("git remote remove origin")
        local("git remote add origin {}".format(distant_repo))
        project_version = local("git describe --long", capture=True)
        print("Getting project version to declare to Sentry ({})".format(project_version))

    return project_version


@do_verbose
def declare_release():
    project_version = env_setup()

    # Create a release
    print("Declaring new release to Sentry")
    local("sentry-cli releases new -p {} {}".format(
        env.application_name,
        project_version
    ))

    # Associate commits with the release
    print("Associating commits with new release for Sentry")
    local("sentry-cli releases set-commits --auto {}".format(project_version))

    # Declare deployment
    print("Declaring new deployment to Sentry")
    local("sentry-cli releases deploys {} new -e {}".format(
        project_version,
        env.goal
    ))
