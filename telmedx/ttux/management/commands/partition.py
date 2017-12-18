from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandParser, CommandError
from django.db.utils import IntegrityError

COMMAND_LIST = 'list'
COMMAND_CREATE = 'create'
COMMAND_SET_PASSWORD = 'set_password'
COMMAND_CHOICES = (COMMAND_CREATE, COMMAND_LIST, COMMAND_SET_PASSWORD)


class Command(BaseCommand):
    help = 'Create\'s a new partition for use within Telmedx'

    def add_arguments(self, parser):
        """
        :param parser:
        :type parser: CommandParser
        :return:
        """
        parser.add_argument('command', type=str, choices=COMMAND_CHOICES)
        parser.add_argument('partition_name', type=str, nargs='?')
        parser.add_argument('--password', '-p', dest='password',
                            type=str, nargs='?')

    def _list(self):
        self.stdout.write('Available partitions:')
        out = []
        for g in Group.objects.all():
            # A partition is defined by a Django `User` object being
            # associated with a `Group` of the same name.
            try:
                g.user_set.get(username=g.name)
                self.stdout.write('\t* {}'.format(g.name))
                out.append(g)
            except User.DoesNotExist:
                pass

        if not len(out):
            print('No partitions found.')

    def _create(self, partition_name, password=None):
        if not partition_name:
            raise CommandError(
                '--name/-n is required if using the create command'
            )
        if not password:
            raise CommandError(
                '--password/-p is required if using the create command'
            )

        try:
            group = Group.objects.create(name=partition_name)
            user = User.objects.create(
                username=partition_name,
                email='{}@local'.format(partition_name)
            )
            user.groups.add(group)
            user.set_password(password)
            user.save()
            self.stdout.write(
                'Partition with the name \'{}\' created'.format(group.name)
            )
        except IntegrityError as e:
            self.stderr.write(
                'Unable to create partition. Try a different name.'
            )
            group = None

    def handle(self, *args, **options):
        command = options.get('command')
        partition_name = options.get('partition_name')
        password = options.get('password')

        if command == COMMAND_LIST:
            self._list()
        elif command == COMMAND_CREATE:
            self._create(partition_name, password)
