import datetime
import json
import os
import subprocess
import sys


class TestFramework:

    def __init__(self, path):
        self.path = path
        self.config_file = None
        self.config_dict = None
        self.suite_list = list()
        self.suite_dict = dict()
        self.config_vars = dict()
        self.output_subdir = "output-{:%Y-%m-%dT%H:%M:%SZ}".format(datetime.datetime.now(datetime.timezone.utc))

    def get_path(self):
        return self.path

    def set_config_file(self, config_file):
        self.config_file = config_file

    def get_config_file(self):
        return self.config_file

    def set_config_data(self, config_dict):
        self.config_dict = config_dict
        if "credentials" in self.config_dict:
            credentials = self.config_dict["credentials"]
            if "username" in credentials:
                self.config_vars["$USERNAME"] = credentials["username"]
            if "password" in credentials:
                self.config_vars["$PASSWORD"] = credentials["password"]
        if "target_system" in self.config_dict:
            self.config_vars["$TARGET_SYSTEM"] = self.config_dict["target_system"]
        if "https" in self.config_dict:
            self.config_vars["$HTTPS"] = self.config_dict["https"]

    def substitute_config_variables(self, test_config_dict):
        if "tests" in test_config_dict:
            tests = test_config_dict["tests"]
            for test_case in tests:
                if "args" in test_case:
                    for index, arg in enumerate(test_case["args"]):
                        if arg in self.config_vars:
                            test_case["args"][index] = self.config_vars[arg]

    def get_config_data(self):
        return self.config_dict

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

    def get_output_subdir(self):
        return self.output_subdir


class TestSuite:

    def __init__(self, path, subdir):
        self.path = os.path.join(path, subdir)
        self.name = subdir
        self.config_file = None
        self.config_dict = None
        self.test_list = list()
        self.test_dict = dict()

    def get_path(self):
        return self.path

    def set_config_file(self, config_file):
        self.config_file = config_file

    def get_config_file(self):
        return self.config_file

    def set_config_data(self, config_dict):
        self.config_dict = config_dict

    def get_config_data(self):
        return self.config_dict

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

    def __init__(self, path, subdir, output_subdir):
        self.path = os.path.join(path, subdir)
        self.name = subdir
        self.output_subdir = os.path.join(self.path, output_subdir)
        self.config_file = None
        self.config_dict = None

    def get_path(self):
        return self.path

    def set_config_file(self, config_file):
        self.config_file = config_file

    def get_config_file(self):
        return self.config_file

    def set_config_data(self, config_dict):
        self.config_dict = config_dict

    def get_config_data(self):
        return self.config_dict

    def get_name(self):
        return self.name

    def get_test_case_path(self):
        return self.path

    def run(self):
        # Change to the directory containing the test case
        try:
            os.chdir(self.path)
        except OSError as e:
            print("Error: Unable to change directory to {}, error: {}".format(self.path, e), file=sys.stderr)
            return
        # Create output directory (should NOT already exist)
        try:
            os.mkdir(self.output_subdir)
        except OSError as e:
            print("Error: Unable to create output directory {}, error: {}".format(self.output_subdir, e),
                  file=sys.stderr)
            return
        # Open output files for STDOUT and STDERR
        try:
            std_out_path = os.path.join(self.output_subdir, "stdout.log")
            std_out_fd = open(std_out_path, "w")
            std_err_path = os.path.join(self.output_subdir, "stderr.log")
            std_err_fd = open(std_err_path, "w")
        except OSError as e:
            print("Error: Unable to create output file in directory {}, error: {}".format(self.output_subdir, e),
                  file=sys.stderr)
            return
        # Run test(s)
        if self.config_dict is not None and "tests" in self.config_dict:
            tests = self.config_dict["tests"]
            for test in tests:
                if "program" in test and "args" in test:
                    args = [test["program"]] + test["args"]
                    try:
                        return_code = subprocess.call(args, stdout=std_out_fd, stderr=std_err_fd)
                        print("return code = {}".format(return_code))
                    except OSError as e:
                        print("Error: OSError while trying  to execute test {}, error: {}".format(args, e),
                              file=sys.stderr)
                    except ValueError as e:
                        print("Error: ValueError while trying  to execute test {}, error: {}".format(args, e),
                              file=sys.stderr)
                    except subprocess.TimeoutExpired as e:
                        print("Error: TimeoutExpired while trying  to execute test {}, error: {}".format(args, e),
                              file=sys.stderr)
                    else:
                        pass
                else:
                    print("Warning: Skipping test in {}: parameter 'program' or 'args' missing from 'tests' element {}"
                          .format(self.name, test))
        else:
            print("Warning: Skipping {}: test config data empty or 'tests' parameter missing. Test config data: {}"
                  .format(self.name, self.config_dict))
        # Close output files
        std_out_fd.close()
        std_err_fd.close()


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


def read_config_file(path, json_file):
    try:
        with open(os.path.join(path, json_file)) as json_data:
            json_dict = json.load(json_data)
        # TODO: Also do schema validation; need schema first
    except OSError as e:
        print("Error opening file {} in directory {}, exception: {}"
              .format(json_file, path, e), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print("Error loading JSON from file {} in directory {}, exception: {}"
              .format(json_file, path, e), file=sys.stderr)
        sys.exit(1)
    else:
        return json_dict


def get_config_file(depth, files):
    config_files = ["framework_conf.json", "suite_conf.json", "test_conf.json"]
    if config_files[depth] in files:
        return config_files[depth]
    return None


def add_details_to_test_case(framework, depth, path, dirs, files):
    _, suite_name, test_name = path.rsplit(os.sep, 2)
    suite = framework.get_suite(suite_name)
    test_case = suite.get_test_case(test_name)
    config_file = get_config_file(depth, files)
    if config_file is not None:
        config_dict = read_config_file(path, config_file)
        test_case.set_config_file(config_file)
        test_case.set_config_data(config_dict)


def add_test_cases_to_suite(framework, depth, path, dirs, files):
    _, suite_name = path.rsplit(os.sep, 1)
    suite = framework.get_suite(suite_name)
    config_file = get_config_file(depth, files)
    if config_file is not None:
        config_dict = read_config_file(path, config_file)
        suite.set_config_file(config_file)
        suite.set_config_data(config_dict)
    for subdir in dirs:
        test_case = TestCase(path, subdir, framework.get_output_subdir())
        suite.add_test_case(test_case)


def add_test_suites(framework, depth, path, dirs, files):
    config_file = get_config_file(depth, files)
    if config_file is not None:
        config_dict = read_config_file(path, config_file)
        framework.set_config_file(config_file)
        framework.set_config_data(config_dict)
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
    if framework.get_config_file() is None:
        print("Error: Top-level config file (framework_conf.json) not found")
    suites = framework.get_suites()
    for suite in suites:
        print("    Suite: name = {}, config_file = {}, path = {}"
              .format(suite.get_name(), suite.get_config_file(), suite.get_path()))
        cases = suite.get_test_cases()
        for case in cases:
            if case.get_config_file() is not None:
                print("        Test case: name = {}, config_file = {}, path = {}"
                      .format(case.get_name(), case.get_config_file(), case.get_path()))
                framework.substitute_config_variables(case.get_config_data())
                print("            test config after substitution: {}".format(case.get_config_data()))
                case.run()
            else:
                print("        Test case: name = {} skipped, config file (test_conf.json) not found, path = {}"
                      .format(case.get_name(), case.get_path()))


if __name__ == "__main__":
    main(sys.argv)
