from btcrpc.utils.log import get_log

__author__ = 'sikamedia'
__Date__ = '2015-01-29'


from django.core.management.base import BaseCommand, CommandError

logger = get_log("transfer bitcoin")


class Command(BaseCommand):

    help = 'Transfer Bitcoin to a predefined address'
    args = '[address]'

    def handle(self, *args, **options):
        logger.info("This is for a trying")
        logger.info(args)
        if args.__len__() == 0:
            logger.info("Take a look at the address defined in configuration")

        elif args.__len__() == 1:
            logger.info(args)
        else:
            logger.info("Here you can not give more than one address")
