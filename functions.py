import subprocess

def execute_shell_command(command):
    try:
        # Execute the shell command
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            # Successful execution
            return result.stdout.decode("utf-8").strip()  # Decode bytes to string
        else:
            # Error occurredhttps://github.com/manunicholasjacob/Testing/blob/main/getbdf2
            return f"Error: {result.stderr.decode('utf-8').strip()}"  # Decode bytes to string
    except Exception as e:
        return f"Error: {str(e)}"
    
def run_command(command):
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()
    if result.returncode != 0:
        raise Exception(f"Command failed with error: {stderr.decode('utf-8')}")
    return stdout.decode('utf-8')

def get_bdf_list():
    """ Get a list of all BDFs using lspci. """
    output = run_command("lspci")
    bdf_list = [line.split()[0] for line in output.splitlines()]
    return bdf_list

def get_vendor_bdf_list(vendor_id):
    """ Get a list of BDFs for a specific vendor using lspci. """
    output = run_command(f"lspci -d {vendor_id}:")
    vendor_bdf_list = [line.split()[0] for line in output.splitlines()]
    return vendor_bdf_list

def get_header_type(bdf):
    header_type = run_command(f"setpci -s {bdf} HEADER_TYPE")
    return header_type.strip()

def get_secondary_bus_number(bdf):
    """ Get the secondary bus number for a given BDF using setpci. """
    secondary_bus_number = run_command(f"setpci -s {bdf} SECONDARY_BUS")
    return secondary_bus_number.strip()

def read_slot_capabilities(bdf):
    try:
        slot_capabilities_output = subprocess.check_output(["setpci", "-s", bdf, "CAP_EXP+0X14.l"])
        return slot_capabilities_output.decode().strip()
    except subprocess.CalledProcessError:
        return None
    
def hex_to_binary(hex_string):
    binary_string = format(int(hex_string, 16), '032b')
    return binary_string

def read_class_code(bdf):
    try:
        class_control = subprocess.check_output(["setpci", "-s", bdf, "09.w"])
        return class_control.decode().strip()
    except subprocess.CalledProcessError:
        return f"Error reading Bridge Control for {bdf}."
    
def identify_gpus():
    command_output = execute_shell_command("lspci | cut -d ' ' -f 1")
    bdf_list = [num for num in command_output.split('\n') if num]
 
    gpus = []
    for bdf in bdf_list:
        class_code = read_class_code(bdf)
        header_type = get_header_type(bdf)
        if class_code and class_code[:2] == '03' and header_type[-2:] == '00':
            gpus.append(bdf)
    return gpus
