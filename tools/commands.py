import os

from git import Repo

from backtesting.collector.data_collector import DataCollector
from config.cst import ORIGIN_URL, VERSION_DEV_PHASE, GIT_ORIGIN
from tools.console_tools import FetchProgressBar
from tools.tentacle_creator.tentacle_creator import TentacleCreator
from tools.tentacle_manager.tentacle_manager import TentacleManager


class Commands:
    @staticmethod
    def update(logger, catch=False):
        logger.info("Updating...")
        try:
            repo = Repo(os.getcwd())
            git = repo.git

            # check origin
            try:
                origin = repo.remote(GIT_ORIGIN)
            except Exception:
                origin = repo.create_remote(GIT_ORIGIN, url=ORIGIN_URL)

            if origin.exists():
                # update
                for fetch_info in origin.pull(progress=FetchProgressBar()):
                    print("Updated %s to %s" % (fetch_info.ref, fetch_info.commit))

                # checkout
                # try:
                #     git.branch(VERSION_DEV_PHASE)
                # except Exception:
                #     repo.create_head(VERSION_DEV_PHASE, origin.refs.VERSION_DEV_PHASE)

                logger.info("Updated")
            else:
                raise Exception("Cannot connect to origin")
        except Exception as e:
            logger.info("Exception raised during updating process... ({})".format(e))
            if not catch:
                raise e

    @staticmethod
    def check_bot_update(logger, log=True):
        repo = Repo(os.getcwd())

        try:
            diff = list(repo.iter_commits('{0}..origin/{0}'.format(repo.active_branch.name)))
            if diff:
                if log:
                    logger.warning("Octobot is not up to date, please use '-u' or '--update' to get the latest release")
                return False
            else:
                if log:
                    logger.info("Octobot is up to date :)")
                return True
        except Exception as e:
            if log:
                logger.warning("Octobot is not up to date, please use '-u' or '--update' to get the latest release")
            return False

    @staticmethod
    def data_collector(config, catch=False):
        data_collector_inst = None
        try:
            data_collector_inst = DataCollector(config)
            data_collector_inst.join()
        except Exception as e:
            data_collector_inst.stop()
            if not catch:
                raise e

    @staticmethod
    def package_manager(config, commands, catch=False):
        try:
            package_manager_inst = TentacleManager(config)
            package_manager_inst.parse_commands(commands)
        except Exception as e:
            if not catch:
                raise e

    @staticmethod
    def tentacle_creator(config, commands, catch=False):
        try:
            tentacle_creator_inst = TentacleCreator(config)
            tentacle_creator_inst.parse_commands(commands)
        except Exception as e:
            if not catch:
                raise e

    @staticmethod
    def start_bot(bot, logger, catch=False):
        bot.create_exchange_traders()
        bot.create_evaluation_threads()
        try:
            bot.start_threads()
            bot.join_threads()
        except Exception as e:
            logger.exception("CryptBot Exception : {0}".format(e))
            if not catch:
                raise e
            Commands.stop_bot(bot)

    @staticmethod
    def stop_bot(bot):
        bot.stop_threads()
        os._exit(0)
