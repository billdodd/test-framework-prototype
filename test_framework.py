import os
import sys


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


def main(argv):
    """
    main
    :param argv: 
    :return: 
    """
    for depth, path, dirs, files in walk_depth(os.getcwd(), 2):
        print("depth {}, directory path: {}".format(depth, path))
        print("files in this directory:")
        for file in files:
            # print("    {}".format(os.path.join(path, file)))
            print("    {}".format(file))
        print("subdirectories in this directory:")
        for subdir in dirs:
            # print("    {}".format(os.path.join(path, subdir)))
            print("    {}".format(subdir))


if __name__ == "__main__":
    main(sys.argv)