import os
from subprocess import run

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandParser, CommandError
from ttux.models import *

AVAILABLE_SITES = ['kpnw', 'mahiri', 'telmedx', ]


class Command(BaseCommand):
    help = 'Builds the site\'s frontend based on environment and site type'

    def add_arguments(self, parser):
        """
        :param parser:
        :type parser: CommandParser
        :return:
        """
        parser.add_argument(
            '--dev',
            action='store_true',
            dest='is_dev',
            help='Build development version',
        )
        parser.add_argument(
            '--prod',
            action='store_true',
            dest='is_prod',
            help='Build production version',
        )
        parser.add_argument(
            '--site', '-s',
            required=True,
            action='store',
            dest='site',
            choices=AVAILABLE_SITES,
            help='Site to build assets for'
        )
        parser.add_argument(
            '--build',
            action='store_const',
            dest='build',
            const='build',
            help='Build frontend -- instead of watch'
        )
        parser.add_argument(
            '--watch',
            action='store_const',
            dest='watch',
            const='watch',
            help='Build and watch frontend -- instead of just build'
        )

    def handle(self, *args, **options):
        is_dev = options.get('is_dev')
        is_prod = options.get('is_prod')
        site = options.get('site')
        build = options.get('build')
        watch = options.get('watch')

        if not any([is_dev, is_prod]):
            raise CommandError('You must choose either --dev or --prod')
        if not any([build, watch]):
            # Default to build if not building or watching
            build = 'build'

        frontend_dir = os.path.join(settings.PROJECT_DIR, 'tel_static', 'brunch')

        # Remove link if it exists, then link active stylesheet to one
        # selected in CLI. Do not show STDOUT, so send to /dev/null
        run(['rm', 'app/styles/_telmedx-active.scss'],
            cwd=frontend_dir, stdout=open(os.devnull, 'wb'))

        # Link file to active scss file
        run(['ln', '-s',
             '_telmedx-{}.scss'.format(site),
             'app/styles/_telmedx-active.scss'],
            cwd=frontend_dir)

        # Run brunch command and compile/build by default
        run(['brunch', watch if watch else build], cwd=frontend_dir)

        if build:
            call_command('collectstatic', '--noinput')
