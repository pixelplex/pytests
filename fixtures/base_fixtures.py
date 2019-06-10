# -*- coding: utf-8 -*-
import random
import string

import lemoncheesecake.api as lcc

NUM_RANGE_1 = 100
NUM_RANGE_2 = 1000
RANGE_OF_STR = 7
RANGE_OF_LENGTH = 5
RANGE_OF_STR_FOR_HEX = 20


@lcc.fixture(scope="test")
def get_random_integer():
    random_int = random.randrange(NUM_RANGE_1, NUM_RANGE_2)
    lcc.log_info("Generated random integer: {}".format(random_int))
    return random_int


@lcc.fixture(scope="test")
def get_random_integer_up_to_hundred():
    random_int = random.randrange(1, 100)
    lcc.log_info("Generated random integer up to a hundred: {}".format(random_int))
    return random_int


@lcc.fixture(scope="test")
def get_random_integer_up_to_fifty():
    random_int = random.randrange(1, 50)
    lcc.log_info("Generated random integer up to a fifty: {}".format(random_int))
    return random_int


@lcc.fixture(scope="test")
def get_random_float():
    random_float = random.uniform(NUM_RANGE_1, NUM_RANGE_2)
    lcc.log_info("Generated random float: {}".format(random_float))
    return random_float


@lcc.fixture(scope="test")
def get_random_float_up_to_hundred():
    random_float = random.uniform(1, 100)
    lcc.log_info("Generated random float up to a hundred: {}".format(random_float))
    return random_float


@lcc.fixture(scope="test")
def get_random_float_up_to_ten():
    random_float = random.uniform(0, 10)
    lcc.log_info("Generated random float up to a ten: {}".format(random_float))
    return random_float


@lcc.fixture(scope="test")
def get_random_string():
    random_string = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(RANGE_OF_STR))
    lcc.log_info("Generated random string: {}".format(random_string))
    return random_string


@lcc.fixture(scope="test")
def get_random_dict():
    random_dict = {}
    random_int = random.randrange(RANGE_OF_LENGTH)
    for i in range(random_int):
        random_dict.update({get_random_string(): get_random_integer()})
    lcc.log_info("Generated random dictionary: {}".format(random_dict))
    return random_dict


@lcc.fixture(scope="test")
def get_random_list():
    random_list = []
    random_int = random.randrange(RANGE_OF_LENGTH)
    probability = random.random()
    for i in range(random_int):
        if probability < 0.33:
            random_list.append(get_random_string())
            continue
        elif 0.33 <= probability < 0.66:
            random_list.append(get_random_integer())
            continue
        else:
            random_list.append(get_random_string())
            random_list.append(get_random_integer())
    lcc.log_info("Generated random list: {}".format(random_list))
    return random_list


@lcc.fixture(scope="test")
def get_random_bool():
    random_bool = bool(random.getrandbits(1))
    lcc.log_info("Generated random bool: {}".format(random_bool))
    return random_bool


@lcc.fixture(scope="test")
def get_all_random_types():
    return {"random_integer": get_random_integer(), "random_float": get_random_float(),
            "random_string": get_random_string(), "random_dict": get_random_dict(),
            "random_list": get_random_list(), "random_bool": get_random_bool()}


@lcc.fixture(scope="test")
def get_random_valid_asset_name():
    random_string = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase) for _ in range(RANGE_OF_STR))
    lcc.log_info("Generated random asset_name: {}".format(random_string))
    return random_string


@lcc.fixture(scope="test")
def get_random_hex_string():
    random_string = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(RANGE_OF_STR_FOR_HEX))
    random_hex_string = ''.join(hex(ord(x))[2:] for x in random_string)
    lcc.log_info("Generated random hex string: {}".format(random_hex_string))
    return random_hex_string


@lcc.fixture(scope="test")
def get_random_valid_account_name():
    random_string = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase) for _ in range(RANGE_OF_STR))
    lcc.log_info("Generated random account_name: {}".format(random_string))
    return random_string


@lcc.fixture(scope="test")
def get_random_character():
    random_character = ''.join(
        random.SystemRandom().choice(string.punctuation))
    lcc.log_info("Generated random punctuation: {}".format(random_character))
    return random_character
