import tempfile
import os


def which(program):

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def get_new_temp_file_path(extension):
    tmp_dir = tempfile._get_default_tempdir()
    tmp_name = next(tempfile._get_candidate_names())
    tmp_file = os.path.join(tmp_dir, tmp_name + "." + extension)
    return tmp_file
