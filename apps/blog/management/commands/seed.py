from django.core.management import BaseCommand, CommandParser, CommandError
from typing import Any
from django.db import transaction
from faker import Faker

class Command(BaseCommand):
    help = "Fill the database with fake data"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users",
            default = 20,
            type = int,
            help = "Number of users to create",
        )

        parser.add_argument(
            "--posts",
            default = 100,
            type=int,
            help="Number of posts to create",
        )

        parser.add_argument(
            "--comments",
            default=500,
            type=int,
            help="Number of comments to create",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding"
        )


    def handle(self, *args: Any, **options: Any) ->None:
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]
        clear: bool = options["clear"]

        for name, value in (("--users", users_count), ("--posts", posts_count), ("--comments", comments_count)):
            if value < 0:
                raise CommandError(f"{name} cannot be less than 0")

        fake = Faker("kk_KZ")


        with transaction.atomic():
            if options["clear"]:
                self.__clear()




    def __clear(self) -> None:
        pass


    def __create_users(self):
        pass

    def __create_posts(self):
        pass

    def __create_comments(self):
        pass