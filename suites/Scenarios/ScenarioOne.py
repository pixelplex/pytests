# -*- coding: utf-8 -*-
import lemoncheesecake.api as lcc
from lemoncheesecake.matching import check_that

from common.base_test import BaseTest

SUITE = {
    "description": "Creating two accounts, make transfer from 1st account to 2nd account, check 2nd account assert"
}

@lcc.prop("main")
@lcc.tags("create two accounts")
@lcc.suite("Check scenario 'create two accounts'")
class ScenarioOne(BaseTest):

    def __init__(self):
        super().__init__()
        self.__database_api_identifier = None



    def setup_suite(self):
        super().setup_suite()
        lcc.set_step("Setup for {}".format(self.__class__.__name__))
        self.__database_api_identifier = self.get_identifier("database")
        lcc.log_info("Database API identifier is '{}'".format(self.__database_api_identifier))



    account_name = "Dima"
    public_key = self.generate_keys()[1]
    #new line

