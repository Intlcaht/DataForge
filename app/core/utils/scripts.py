def rn_scrpt(file, args): 
    """
    Run a shell script with the given filename and arguments.
    
    Parameters:
        file (str): The name of the shell script file to run.
        args (list): A list of arguments to pass to the script.
    
    Returns:
        int: The return code from the executed script, typically 0 if successful.
    """

    import os  

    # Get the current working directory where this script is being run.
    # This is used as the base path to locate shell scripts.
    current_directory = os.getcwd()
    # Join the current directory path with the provided file name
    # to get the full path to the script file.
    script_path = os.path.join(current_directory, file)

    # Importing logging for debugging and monitoring execution
    import logging

    # Import utility functions from a sibling shell module:
    # - execute_command: actually runs the command in a subprocess
    # - prepare_command_for_shell: prepares the command string with shell formatting
    # - set_verbosity: sets how much output you see (debug/info/warning/etc.)
    from .shell import execute_command, prepare_command_for_shell, set_verbosity 

    # Set the logging level to DEBUG so that all debug messages are shown
    # This is helpful during development or troubleshooting
    set_verbosity(logging.DEBUG)

    # Prepare the command to be executed in the shell
    # The shell type is set to 'auto' so it auto-detects whether to use bash, sh, etc.
    # The 'verbose=True' flag ensures extra logging/info will be printed
    command = prepare_command_for_shell(
        script_path=script_path,  # Full path to the script
        cmd=None,                 # No custom command; we'll run the script directly
        args=args,                # Arguments to pass to the script
        shell_type='auto',        # Automatically determine which shell to use
        verbose=True              # Enable verbose output for debugging
    )  

    # Execute the command in a subprocess
    # 'shell=True' allows shell features like piping and redirection
    # 'verbose=True' means output from the command will be shown in the terminal/log
    result = execute_command(command, shell=True, verbose=True)    

    # Return the return code from the command
    # Useful to determine if the script ran successfully (0) or failed (non-zero)
    return result.returncode

def run_env_gen(args):
    """
    Shortcut function to run the env gen script.

    Parameters:
        args (list): Arguments to pass to the env gen script.

    Returns:
        int: The return code of the script execution.
    """

    # Call the generic run_script() with the specific env gen script path
    return rn_scrpt('scripts/env_yaml_gen.sh', args)
    
def run_db_mng(args):
    """
    Shortcut function to run the database management shell script.

    Parameters:
        args (list): Arguments to pass to the db management script.

    Returns:
        int: The return code of the script execution.
    """

    # Call the generic run_script() with the specific db management script path
    return rn_scrpt('scripts/dbmng.sh', args)

def run_db_ctl(args):
    """
    Shortcut function to run the database control shell script.

    Parameters:
        args (list): Arguments to pass to the db control script.

    Returns:
        int: The return code of the script execution.
    """

    # Call the generic run_script() with the specific db control script path
    return rn_scrpt('dbctl.sh', args)
