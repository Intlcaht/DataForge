
def rn_scrpt(file, args): 
    """
    Run a shell script located in the current working directory with the given arguments.
    
    Parameters:
    ----------
    file : str
        The name of the shell script file to run. This can be relative or absolute.
    args : list
        A list of command-line arguments to pass to the script.

    Returns:
    -------
    int
        The return code from the executed script. A return code of 0 generally indicates success.

    Example usage:
    -------------
    # Assuming you have a script named 'deploy.sh' in the current directory
    rn_scrpt("deploy.sh", ["--env", "production", "--force"])

    # This will execute the equivalent of:
    #   ./deploy.sh --env production --force
    # With debug output enabled
    """

    import os

    # Get the current working directory where this script is being run.
    # This directory will be used as the base path to locate the shell script.
    current_directory = os.getcwd()

    # Combine the current directory with the provided script filename
    # to construct the absolute path to the script.
    script_path = os.path.join(current_directory, file)

    # Import Python's logging module for setting verbosity levels
    import logging

    # Import shell utilities from sibling module:
    # - execute_command: runs the command and returns a result object with returncode
    # - prepare_command_for_shell: constructs a valid shell command string from input
    # - set_verbosity: enables logging at different levels (e.g., DEBUG, INFO)
    from .shell import execute_command, prepare_command_for_shell, set_verbosity

    # Enable DEBUG-level verbosity to get detailed logs of each step.
    # This is particularly useful during testing, CI/CD, or troubleshooting.
    set_verbosity(logging.DEBUG)

    # Prepare the full shell command using the helper function.
    # Arguments:
    # - script_path: Absolute path to the script to be executed
    # - cmd: None means the script itself is the command
    # - args: Additional arguments to be passed to the script
    # - shell_type: 'auto' allows the system to choose the most appropriate shell (bash, sh, etc.)
    # - verbose: Enables more descriptive output of what's being run
    command = prepare_command_for_shell(
        script_path=script_path,
        cmd=None,
        args=args,
        shell_type='auto',
        verbose=True
    )

    # Execute the prepared shell command using the subprocess wrapper.
    # shell=True allows support for advanced shell features like piping (|), redirection (>), etc.
    # verbose=True prints the command and its output to the console/log.
    result = execute_command(command, shell=True, verbose=True)

    # Return the exit code from the command execution.
    # A value of 0 means success; any non-zero value indicates failure.
    return result.returncode

def rn_pyscrpt(args): 
    """
    rn_pyscrpt: Execute a dynamically cleaned Python command string in a subprocess.

    This function receives a raw command string (usually generated by a script executor),
    cleans it up into a valid shell command, and executes it using a subprocess.

    It handles:
    - Nested list flattening
    - Safe parsing of Python-style argument strings
    - Logging and verbosity control

    Example usage:
    --------------
    Given a raw input command like:
        args = "'scripts/obfuscator_env.py ', ['-i dbstack/.env.gen -o secret.env -p secret']"

    Call:
        rn_pyscrpt(args)

    This internally constructs:
        python scripts/obfuscator_env.py -i dbstack/.env.gen -o secret.env -p secret

    Then executes the command and returns the subprocess's return code.

    Typical input strings:
    - "Executing command: python ['script.py', ['--flag1', 'value1'], ['--flag2', 'value2']]"
    - "Executing command: echo ['Hello, World!']"
    - "Executing command: python ['script.py', ['--option', 'value with spaces']]"
    """
    import logging
    from .shell import execute_command, set_verbosity 
    from .utils import flatten_list
    set_verbosity(logging.DEBUG)

    import re
    import ast

    def clean_command(command_str):
        """
        Extract and sanitize a command from a raw Python-evaluated string.

        Example:
            "python ['script.py', ['--option', 'value']]" 
            -> "python script.py --option value"

        Handles:
        - Matching command and arguments using regex
        - Evaluating Python list-like syntax using ast.literal_eval
        - Flattening any nested argument lists
        """
        match = re.match(r"(\w+)\s*(.*)", command_str)
        if match:
            command = match.group(1)
            args_str = match.group(2).strip()

            try:
                # Wrap args_str in brackets to evaluate as a list
                args_list = ast.literal_eval(f"[{args_str}]")
                if isinstance(args_list, list):
                    args_list = flatten_list(args_list)
            except (SyntaxError, ValueError):
                # If the arguments can't be parsed, default to empty list
                args_list = []

            # Construct command string by joining the command and arguments
            cleaned_command = f"{command} {' '.join(map(str, args_list))}"
            return cleaned_command.strip()

        # If no match was found, return stripped original string
        return command_str.strip()

    # Construct and execute cleaned command
    # Use shell=True to allow full shell features (e.g., redirection, pipes)
    # verbose=True to display the output in logs
    result = execute_command(clean_command(f"python {args}"), shell=True, verbose=True)    

    # Return the subprocess's return code (0 = success)
    return result.returncode

def run_env_gen(args):
    return rn_scrpt('scripts/env_yaml_gen.sh', args)
    
def run_db_mng(args):
    return rn_scrpt('scripts/dbmng.sh', args)

def run_db_ctl(args):
    return rn_scrpt('dbctl.sh', args)

def run_db_ctl_rc(args):
    return rn_scrpt('sys/local/dbctl.rc.sh -d sys/local', args)

def run_obfuscator_env(args):
    return rn_pyscrpt(['scripts/obfuscator_env.py ', args])

def run_obfuscator_json(args):
    return rn_pyscrpt(['scripts/obfuscator_json.py ', args])

def run_obfuscator_yml(args):
    return rn_pyscrpt(['scripts/obfuscator_yml.py ', args])

def run_extract_deps(args):
    return rn_pyscrpt(['scripts/extract_deps.py ', args])
