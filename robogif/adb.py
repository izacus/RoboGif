import subprocess

# Commands regarding ADB
def get_devices():
    devices = {}

    adb_proc = subprocess.Popen(['adb', 'devices', '-l'], stdout=subprocess.PIPE)
    while True:
        line = adb_proc.stdout.readline().strip().decode("utf-8")
        if line != '':
            #the real code does filtering here
            if line.startswith("List of"):
                continue
            split_line = line.split()
            if len(split_line) < 2:
                continue
            if split_line[1] != 'device':
                continue
            device_id = split_line[0]
            param_dict = {}
            for param in split_line:
                if ':' in param:
                    split_param = param.split(':')
                    if len(split_param) < 2:
                        continue
                    param_dict[split_param[0]] = split_param[1]
            devices[device_id] = param_dict
        else:
            break

    return devices
