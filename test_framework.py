import os
import sys


class TestFramework:

    def __init__(self, path):
        self.path = path
        self.config_file = None
        self.suite_list = list()
        self.suite_dict = dict()

    def get_path(self):
        return self.path

    def set_config_file(self, config_file):
        self.config_file = config_file

    def get_config_file(self):
        return self.config_file

    def add_suite(self, test_suite):
        self.suite_list.append(test_suite)
        name = test_suite.get_name()
        self.suite_dict[name] = test_suite

    def get_suite(self, name):
        if name in self.suite_dict:
            return self.suite_dict[name]
        else:
            return None

    def get_suites(self):
        return self.suite_list


class TestSuite:

    def __init__(self, path, subdir):
        self.path = os.path.join(path, subdir)
        self.name = subdir
        self.config_file = None
        self.test_list = list()
        self.test_dict = dict()

    def get_path(self):
        return self.path

    def set_config_file(self, config_file):
        self.config_file = config_file

    def get_config_file(self):
        return self.config_file

    def get_name(self):
        return self.name

    def add_test_case(self, test_case):
        self.test_list.append(test_case)
        name = test_case.get_name()
        self.test_dict[name] = test_case

    def get_test_case(self, name):
        if name in self.test_dict:
            return self.test_dict[name]
        else:
            return None

    def get_test_cases(self):
        return self.test_list


class TestCase:

    def __init__(self, path, subdir):
        self.path = os.path.join(path, subdir)
        self.name = subdir
        self.config_file = None

    def get_path(self):
        return self.path

    def set_config_file(self, config_file):
        self.config_file = config_file

    def get_config_file(self):
        return self.config_file

    def get_name(self):
        return self.name


def walk_depth(directory, max_depth=1):
    """
    walk_depth
    :param directory: 
    :param max_depth: 
    :return: 
    """
    directory = directory.rstrip(os.path.sep)
    assert os.path.isdir(directory)
    base_sep = directory.count(os.path.sep)
    for path, dirs, files in os.walk(directory):
        cur_sep = path.count(os.path.sep)
        depth = cur_sep - base_sep
        yield depth, path, dirs, files
        if depth >= max_depth:
            del dirs[:]


def display_entry(depth, path, dirs, files):
    print("depth {}, directory path: {}".format(depth, path))
    print("files in this directory:")
    for file in files:
        print("    {}".format(file))
    print("subdirectories in this directory:")
    for subdir in dirs:
        print("    {}".format(subdir))


def get_config_file(files):
    for file in files:
        if file.endswith("_conf.json"):
            return file
    return None


def add_details_to_test_case(framework, depth, path, dirs, files):
    _, suite_name, test_name = path.rsplit(os.sep, 2)
    suite = framework.get_suite(suite_name)
    test_case = suite.get_test_case(test_name)
    config_file = get_config_file(files)
    test_case.set_config_file(config_file)


def add_test_cases_to_suite(framework, depth, path, dirs, files):
    _, suite_name = path.rsplit(os.sep, 1)
    suite = framework.get_suite(suite_name)
    config_file = get_config_file(files)
    suite.set_config_file(config_file)
    for subdir in dirs:
        test_case = TestCase(path, subdir)
        suite.add_test_case(test_case)


def add_test_suites(framework, depth, path, dirs, files):
    config_file = get_config_file(files)
    framework.set_config_file(config_file)
    for subdir in dirs:
        suite = TestSuite(path, subdir)
        framework.add_suite(suite)


def main(argv):
    """
    main
    :param argv: 
    :return: 
    """
    framework = None
    for depth, path, dirs, files in walk_depth(os.getcwd(), 2):
        # display_entry(depth, path, dirs, files)
        if depth == 0:
            framework = TestFramework(path)
            add_test_suites(framework, depth, path, dirs, files)
        elif depth == 1:
            add_test_cases_to_suite(framework, depth, path, dirs, files)
        elif depth == 2:
            add_details_to_test_case(framework, depth, path, dirs, files)
        else:
            print("Error: invalid depth {}".format(depth), file=sys.stderr)
            exit(1)

    print("Test Framework: config_file = {}, path = {}".format(framework.get_config_file(), framework.get_path()))
    suites = framework.get_suites()
    for suite in suites:
        if suite.get_config_file() is not None:
            print("    Suite: name = {}, config_file = {}, path = {}"
                  .format(suite.get_name(), suite.get_config_file(), suite.get_path()))
            cases = suite.get_test_cases()
            for case in cases:
                if case.get_config_file() is not None:
                    print("        Testcase: name = {}, config_file = {}, path = {}"
                          .format(case.get_name(), case.get_config_file(), case.get_path()))


if __name__ == "__main__":
    main(sys.argv)