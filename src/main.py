import glob
import os
import shutil
import zipfile


def rename(path, rm_dirs=False, rm_zips=False):
    if os.path.isdir(path):
        print(path)

        # replace backslash with forward slash so all paths are the same for windows, osx, linux
        path = path.replace("\\", "/")

        # iterate over sub directories
        for dir in glob.glob(path + "*/"):

            # unzip all files in subdirectories
            unzip(dir, rm_zips)

            # get name of directory
            # replace backslash with forward slash so all paths are the same for windows, osx, linux
            dir_name = dir.replace("\\", "/").split("/")[-2]

            # iterate over every file in sub directory
            for file in glob.glob(dir + "*"):
                # get name of file
                file_name = os.path.basename(file)

                # move file to outer path and rename file with prefix (dir_name_file_name)
                print("moving", path + dir_name + "_" + file_name)
                shutil.move(file, path + dir_name + "_" + file_name)

        if rm_dirs:
            remove_empty_folders(path)

    else:
        raise ValueError("The path specified was empty or not a directory")


def remove_empty_folders(path):
    # iterate over sub directories
    for dir in glob.glob(path + "*"):
        # double check path is subdirectory and empty
        if os.path.isdir(dir) and not os.listdir(dir):
            print("removing empty directory", dir)
            os.rmdir(dir)


def unzip(path, rm=False):
    '''
    Input: path where dir with zips, rm=True to delete zips after extraction
    Output: contents of zip file in path specified
    '''

    for file in glob.glob(path + "*.zip"):
        # extract zip to path
        zipfile.ZipFile(file).extractall(path)

        if rm:
            # remove zip after extraction
            os.remove(file)

    # # while there are zips or folders in the path
    # contents = True
    # while contents:
    #     contents = [file for file in glob.glob(path + "*") if file in glob.glob(path + "*.zip") or os.path.isdir(file)]
    #
    #     # iterate over zips and directories
    #     for file in contents:
    #         print(file)
    #
    #         # if the file is a zip, extract and then delete it
    #         if file.endswith(".zip"):
    #             zipfile.ZipFile(file).extractall(path)
    #             os.remove(file)
    #
    #         # if the file is a directory, move files out of it, then delete it
    #         elif os.path.isdir(file):
    #
    #             # add / because file is really a directory
    #             for sub_file in glob.glob(file + "/*"):
    #                 file_name = os.path.basename(sub_file)
    #                 shutil.move(sub_file, path + "/" + file_name)
    #             os.rmdir(file)

#
# if __name__ == "__main__":
#     rename("C:/Users/conor/Documents/GitHub/CompCorrector/outer/test/", rm_dirs=True)