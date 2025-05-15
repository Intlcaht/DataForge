# import fcntl
import logging
import os
import re
import shlex
import shutil
import subprocess
import time
import select
import sys
import signal
import threading
from typing import Union, Optional, Dict, List, Callable, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("shell_utils")

class ShellExecutionError(Exception):
    """
    Custom exception class raised when a shell command execution fails.
    
    This exception provides detailed information about the failed command, including:
    - The exact command that was executed
    - The return code from the command
    - Standard output (if captured)
    - Standard error (if captured)
    
    Inherits from the base Exception class to integrate with Python's error handling system.
    """

    def __init__(self, cmd: str, return_code: int, stdout: str = "", stderr: str = ""):
        """
        Initialize the ShellExecutionError with details about the failed command.
        
        Args:
            cmd (str): The shell command that was executed and failed
            return_code (int): The exit/return code from the command (non-zero indicates failure)
            stdout (str, optional): The captured standard output from the command. Defaults to "".
            stderr (str, optional): The captured standard error from the command. Defaults to "".
            
        The constructor stores all execution details as instance attributes and formats
        a comprehensive error message that includes:
        - The failed command
        - The return code
        - The stderr output (if available)
        """
        
        # Store the executed command as an instance attribute
        self.cmd = cmd
        
        # Store the command's return code (non-zero typically indicates failure)
        self.return_code = return_code
        
        # Store the captured standard output (if any)
        self.stdout = stdout
        
        # Store the captured standard error (if any)
        self.stderr = stderr
        
        # Begin constructing the base error message with command and return code
        message = f"Command '{cmd}' failed with return code {return_code}"
        
        # Append standard error to the message if it exists
        # This provides immediate visibility into what went wrong
        if stderr:
            message += f"\nStandard Error: {stderr}"
            
        # Initialize the parent Exception class with our constructed message
        # This ensures:
        # 1. Proper exception chaining
        # 2. Correct string representation when printed
        # 3. Full integration with Python's exception handling system
        super().__init__(message)

def set_verbosity(level: int) -> None:
    """
    Set the verbosity level for the shell utilities module.

    Args:
        level (int): Logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)
    """
    logger.setLevel(level)
    logger.debug(f"Verbosity level set to {level}")

def normalize_path_for_shell(path: str, target_shell: str = 'auto') -> str:
    """
    Normalize file paths for different shell environments.

    Args:
        path: The file path to normalize
        target_shell: Target shell environment ('auto', 'cmd', 'powershell', 'git_bash', 'wsl', 'posix')
                     'auto' will detect the current environment and choose appropriately

    Returns:
        Normalized path string suitable for the target shell environment
    """
    # Detect target shell if set to auto
    if target_shell == 'auto':
        if os.name == 'nt':  # Windows
            # Check if running in Git Bash
            try:
                result = subprocess.run(
                    ["bash", "-c", "echo $BASH_VERSION"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=1
                )
                if result.returncode == 0 and result.stdout:
                    target_shell = 'git_bash'
                else:
                    result = subprocess.run(
                        ["powershell", "-Command", "echo $PSVersionTable.PSVersion"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=1
                    )
                    target_shell = 'powershell' if result.returncode == 0 else 'cmd'
            except (subprocess.SubprocessError, FileNotFoundError):
                target_shell = 'cmd'
        else:
            target_shell = 'posix'

    norm_path = os.path.normpath(path)

    if target_shell in ('cmd', 'powershell'):
        return norm_path
    elif target_shell == 'git_bash':
        posix_path = norm_path.replace('\\', '/')
        drive_letter_match = re.match(r'^([a-zA-Z]):(.+)$', posix_path)
        if drive_letter_match:
            drive_letter = drive_letter_match.group(1).lower()
            rest_of_path = drive_letter_match.group(2)
            return f"/{drive_letter}{rest_of_path}"
        return posix_path
    elif target_shell == 'wsl':
        posix_path = norm_path.replace('\\', '/')
        drive_letter_match = re.match(r'^([a-zA-Z]):(.+)$', posix_path)
        if drive_letter_match:
            drive_letter = drive_letter_match.group(1).lower()
            rest_of_path = drive_letter_match.group(2)
            return f"/mnt/{drive_letter}{rest_of_path}"
        return posix_path
    elif target_shell == 'posix':
        return norm_path.replace('\\', '/')

    return norm_path

def prepare_command_for_shell(
    cmd: str,
    script_path: str = None,
    args: list = None,
    shell_type: str = 'auto',
    verbose: bool = False
) -> str:
    """
    Prepare a command string for execution in the target shell environment.

    Args:
        cmd: The command to execute (or None to build from script_path and args)
        script_path: Path to script file (if cmd is None)
        args: List of arguments to pass to the script (if cmd is None)
        shell_type: Target shell ('auto', 'cmd', 'powershell', 'git_bash', 'wsl', 'bash', 'sh')
        verbose: Whether to log detailed information

    Returns:
        Prepared command string ready for execution
    """
    if cmd is None:
        if script_path is None:
            raise ValueError("Either cmd or script_path must be provided")
        cmd = script_path
        if args:
            cmd = f"{script_path} {' '.join(str(arg) for arg in args)}"

    if shell_type == 'auto':
        if os.name == 'nt':
            git_bash = r"C:\Program Files\Git\bin\bash.exe"
            if os.path.exists(git_bash):
                shell_type = 'git_bash'
            else:
                try:
                    result = subprocess.run(
                        ["wsl", "echo", "available"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=1
                    )
                    shell_type = 'wsl' if result.returncode == 0 else 'cmd'
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass
                    # shell_type = 'cmd'
        else:
            shell_type = 'bash' if os.path.exists("/bin/bash") or os.path.exists("/usr/bin/bash") else 'sh'

    if verbose:
        logger.debug(f"Preparing command for shell type: {shell_type}")
        logger.debug(f"Original command: {cmd}")

    if script_path is None and ' ' in cmd:
        script_path = cmd.split(' ')[0]

    if shell_type == 'cmd':
        return cmd
    elif shell_type == 'powershell':
        ps_cmd = cmd.replace("'", "''")
        return f'powershell -Command "{ps_cmd}"'
    elif shell_type == 'git_bash':
        git_bash_exe = r"C:\Program Files\Git\bin\bash.exe"
        if script_path and ':' in script_path:
            normalized_path = normalize_path_for_shell(script_path, 'git_bash')
            cmd = cmd.replace(script_path, normalized_path)
        return f'"{git_bash_exe}" -c "{cmd.replace("\"", "\\\"")}"'
    elif shell_type == 'wsl':
        if script_path and ':' in script_path:
            normalized_path = normalize_path_for_shell(script_path, 'wsl')
            cmd = cmd.replace(script_path, normalized_path)
        return f'wsl bash -c "{cmd.replace("\"", "\\\"")}"'
    elif shell_type == 'bash':
        return f'bash -c "{cmd.replace("\"", "\\\"")}"'
    elif shell_type == 'sh':
        return f'sh -c "{cmd.replace("\"", "\\\"")}"'

    return cmd

def which_shell_available() -> str:
    """
    Detect which shell environments are available on the system.

    Returns:
        String describing the available shell environments
    """
    from shutil import which

    available_shells = []
    details = []

    for shell in ['bash', 'sh', 'zsh', 'fish', 'cmd', 'powershell']:
        if which(shell):
            available_shells.append(shell)

    if os.name == 'nt':
        if os.path.exists(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"):
            if 'powershell' not in available_shells:
                available_shells.append('powershell')

        git_bash = r"C:\Program Files\Git\bin\bash.exe"
        if os.path.exists(git_bash):
            available_shells.append('git_bash')
            try:
                result = subprocess.run(
                    [git_bash, "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=1,
                    text=True
                )
                if result.returncode == 0:
                    details.append(f"Git Bash: {result.stdout.strip()}")
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

        try:
            result = subprocess.run(
                ["wsl", "--list", "--verbose"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=1,
                text=True
            )
            if result.returncode == 0:
                available_shells.append('wsl')
                details.append(f"WSL: {result.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    for shell in available_shells:
        if shell not in ['git_bash', 'wsl']:
            try:
                version_flag = "--version"
                if shell == 'cmd':
                    continue
                result = subprocess.run(
                    [shell, version_flag],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=1,
                    text=True
                )
                if result.returncode == 0:
                    version_info = result.stdout.strip().split('\n')[0]
                    details.append(f"{shell}: {version_info}")
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

    if not available_shells:
        return "No shells detected"

    return f"Available shells: {', '.join(available_shells)}\n" + '\n'.join(details)

def execute_command(
    cmd: Union[str, List[str]],
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    check: bool = False,
    capture_output: bool = True,
    encoding: str = 'utf-8',
    verbose: bool = False
) -> subprocess.CompletedProcess:
    """
    Execute a shell command and return the result.

    Args:
        cmd: Command string or list of command arguments
        shell: Whether to execute command through the shell
        cwd: Working directory for the command
        env: Environment variables for the command
        timeout: Maximum execution time in seconds
        check: Whether to raise an exception if command fails
        capture_output: Whether to capture stdout and stderr
        encoding: Character encoding for output
        verbose: Whether to log detailed information about execution

    Returns:
        subprocess.CompletedProcess object with execution results

    Raises:
        ShellExecutionError: If check=True and the command returns non-zero
        TimeoutExpired: If command execution exceeds timeout
    """
    
    if not shell and isinstance(cmd, str):
        cmd = shlex.split(cmd)

    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
    if verbose:
        logger.info(f"Executing command: {cmd_str}")
        if cwd:
            logger.info(f"Working directory: {cwd}")
        if env:
            logger.info(f"Environment variables: {env}")

    try:
        stdout = subprocess.PIPE if capture_output else None
        stderr = subprocess.PIPE if capture_output else None

        start_time = time.time()
        result = subprocess.run(
            cmd,
            shell=shell,
            cwd=cwd,
            env=env,
            check=False,
            timeout=timeout,
            stdout=stdout,
            stderr=stderr,
            text=True,
            encoding=encoding
        )
        execution_time = time.time() - start_time

        if verbose:
            logger.info(f"Command completed in {execution_time:.2f}s with return code {result.returncode}")
            if capture_output and result.stdout and len(result.stdout) > 0:
                logger.debug(f"STDOUT: {result.stdout.strip()}")
            if capture_output and result.stderr and len(result.stderr) > 0:
                logger.debug(f"STDERR: {result.stderr.strip()}")

        if check and result.returncode != 0:
            stdout_str = result.stdout if result.stdout else ""
            stderr_str = result.stderr if result.stderr else ""
            raise ShellExecutionError(cmd_str, result.returncode, stdout_str, stderr_str)

        return result

    except subprocess.TimeoutExpired as e:
        if verbose:
            logger.error(f"Command timed out after {timeout}s: {cmd_str}")
        raise
    except Exception as e:
        if verbose:
            logger.error(f"Error executing command: {cmd_str}\n{str(e)}")
        raise

def execute_with_input(
    cmd: Union[str, List[str]],
    input_data: str,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    encoding: str = 'utf-8',
    verbose: bool = False
) -> subprocess.CompletedProcess:
    """
    Execute a command and provide input data to it.

    Args:
        cmd: Command string or list of command arguments
        input_data: String data to send to process's stdin
        shell: Whether to execute command through the shell
        cwd: Working directory for the command
        env: Environment variables for the command
        timeout: Maximum execution time in seconds
        encoding: Character encoding for input/output
        verbose: Whether to log detailed information about execution

    Returns:
        subprocess.CompletedProcess object with execution results
    """
    if not shell and isinstance(cmd, str):
        cmd = shlex.split(cmd)

    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
    if verbose:
        logger.info(f"Executing command with input: {cmd_str}")
        logger.debug(f"Input data: {input_data}")

    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            shell=shell,
            cwd=cwd,
            env=env,
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding=encoding
        )

        if verbose:
            logger.info(f"Command completed with return code {result.returncode}")
            if result.stdout:
                logger.debug(f"STDOUT: {result.stdout.strip()}")
            if result.stderr:
                logger.debug(f"STDERR: {result.stderr.strip()}")

        return result

    except Exception as e:
        if verbose:
            logger.error(f"Error executing command with input: {cmd_str}\n{str(e)}")
        raise

def execute_interactive(
    cmd: Union[str, List[str]],
    input_handler: Optional[Callable[[str, Any], Optional[str]]] = None,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    encoding: str = 'utf-8',
    verbose: bool = False,
    context: Any = None
) -> Tuple[int, str, str]:
    """
    Execute a command interactively, allowing dynamic input based on output.

    Args:
        cmd: Command string or list of command arguments
        input_handler: Callback function that receives output and returns input to send
                      Function signature: (output_line: str, context: Any) -> Optional[str]
        shell: Whether to execute command through the shell
        cwd: Working directory for the command
        env: Environment variables for the command
        timeout: Maximum execution time in seconds
        encoding: Character encoding for input/output
        verbose: Whether to log detailed information
        context: Optional context object passed to input_handler

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    if not shell and isinstance(cmd, str):
        cmd = shlex.split(cmd)

    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
    if verbose:
        logger.info(f"Starting interactive command: {cmd_str}")

    process = subprocess.Popen(
        cmd,
        shell=shell,
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding=encoding,
        bufsize=1
    )

    stdout_data = []
    stderr_data = []
    start_time = time.time()

    try:
        fcntl.fcntl(process.stdout, fcntl.F_SETFL, os.O_NONBLOCK) # type: ignore
        fcntl.fcntl(process.stderr, fcntl.F_SETFL, os.O_NONBLOCK) # type: ignore

        while process.poll() is None:
            if timeout and (time.time() - start_time > timeout):
                process.kill()
                raise subprocess.TimeoutExpired(cmd_str, timeout)

            readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)

            for stream in readable:
                line = stream.readline()
                if not line:
                    continue

                if stream == process.stdout:
                    stdout_data.append(line)
                    if verbose:
                        logger.debug(f"STDOUT: {line.strip()}")

                    if input_handler:
                        response = input_handler(line, context)
                        if response is not None:
                            if verbose:
                                logger.debug(f"Sending input: {response}")
                            process.stdin.write(f"{response}\n")
                            process.stdin.flush()

                elif stream == process.stderr:
                    stderr_data.append(line)
                    if verbose:
                        logger.debug(f"STDERR: {line.strip()}")

        stdout, stderr = process.communicate()
        if stdout:
            stdout_data.append(stdout)
        if stderr:
            stderr_data.append(stderr)

        return_code = process.returncode
        full_stdout = "".join(stdout_data)
        full_stderr = "".join(stderr_data)

        if verbose:
            duration = time.time() - start_time
            logger.info(f"Interactive command completed in {duration:.2f}s with return code {return_code}")

        return return_code, full_stdout, full_stderr

    except Exception as e:
        if process.poll() is None:
            process.kill()
        if verbose:
            logger.error(f"Error during interactive command: {cmd_str}\n{str(e)}")
        raise

def execute_parallel_commands(
    commands: List[Union[str, List[str]]],
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    max_workers: int = None,
    timeout: Optional[float] = None,
    verbose: bool = False
) -> List[subprocess.CompletedProcess]:
    """
    Execute multiple commands in parallel and return their results.

    Args:
        commands: List of commands to execute
        shell: Whether to execute commands through the shell
        cwd: Working directory for the commands
        env: Environment variables for the commands
        max_workers: Maximum number of parallel processes
        timeout: Maximum execution time in seconds
        verbose: Whether to log detailed information

    Returns:
        List of subprocess.CompletedProcess objects with execution results
    """
    import concurrent.futures

    if verbose:
        logger.info(f"Executing {len(commands)} commands in parallel")

    def _execute_single(cmd):
        return execute_command(
            cmd=cmd,
            shell=shell,
            cwd=cwd,
            env=env,
            timeout=timeout,
            check=False,
            capture_output=True,
            verbose=verbose
        )

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_cmd = {
            executor.submit(_execute_single, cmd): cmd
            for cmd in commands
        }

        for future in concurrent.futures.as_completed(future_to_cmd):
            cmd = future_to_cmd[future]
            try:
                result = future.result()
                results.append(result)
                if verbose:
                    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
                    logger.info(f"Command completed: {cmd_str} (code: {result.returncode})")
            except Exception as e:
                if verbose:
                    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
                    logger.error(f"Command failed: {cmd_str} - {str(e)}")
                results.append(None)

    return results

def execute_pipeline(
    commands: List[Union[str, List[str]]],
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    verbose: bool = False
) -> Tuple[int, str, str]:
    """
    Execute a pipeline of commands where output of each feeds into input of next.

    Args:
        commands: List of commands to execute in sequence
        shell: Whether to execute commands through the shell
        cwd: Working directory for the commands
        env: Environment variables for the commands
        timeout: Maximum execution time in seconds
        verbose: Whether to log detailed information

    Returns:
        Tuple of (final_return_code, final_stdout, combined_stderr)
    """
    if not commands:
        raise ValueError("No commands provided for pipeline execution")

    if verbose:
        pipeline_str = " | ".join([cmd if isinstance(cmd, str) else " ".join(cmd) for cmd in commands])
        logger.info(f"Executing pipeline: {pipeline_str}")

    start_time = time.time()
    combined_stderr = []

    if len(commands) == 1:
        result = execute_command(
            commands[0],
            shell=shell,
            cwd=cwd,
            env=env,
            timeout=timeout,
            verbose=verbose
        )
        return result.returncode, result.stdout, result.stderr

    prev_cmd = commands[0]
    if not shell and isinstance(prev_cmd, str):
        prev_cmd = shlex.split(prev_cmd)

    prev_process = subprocess.Popen(
        prev_cmd,
        shell=shell,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    processes = [prev_process]

    for cmd in commands[1:-1]:
        if not shell and isinstance(cmd, str):
            cmd = shlex.split(cmd)

        stderr_data = prev_process.stderr.read()
        if stderr_data:
            combined_stderr.append(stderr_data)

        current_process = subprocess.Popen(
            cmd,
            shell=shell,
            cwd=cwd,
            env=env,
            stdin=prev_process.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        processes.append(current_process)
        prev_process.stdout.close()
        prev_process = current_process

    last_cmd = commands[-1]
    if not shell and isinstance(last_cmd, str):
        last_cmd = shlex.split(last_cmd)

    last_process = subprocess.Popen(
        last_cmd,
        shell=shell,
        cwd=cwd,
        env=env,
        stdin=prev_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    processes.append(last_process)
    prev_process.stdout.close()

    def _check_timeout():
        if timeout and (time.time() - start_time > timeout):
            for p in processes:
                if p.poll() is None:
                    p.kill()
            raise subprocess.TimeoutExpired(str(commands), timeout)

    while last_process.poll() is None:
        _check_timeout()
        time.sleep(0.1)

    final_stdout, final_stderr = last_process.communicate()
    if final_stderr:
        combined_stderr.append(final_stderr)

    for p in processes[:-1]:
        if p.stderr:
            stderr_data = p.stderr.read()
            if stderr_data:
                combined_stderr.append(stderr_data)

    if verbose:
        execution_time = time.time() - start_time
        logger.info(f"Pipeline completed in {execution_time:.2f}s with return code {last_process.returncode}")
        if final_stdout:
            logger.debug(f"Final STDOUT: {final_stdout.strip()}")
        if combined_stderr:
            logger.debug(f"Combined STDERR: {''.join(combined_stderr).strip()}")

    return last_process.returncode, final_stdout, "".join(combined_stderr)

def get_user_input(
    prompt: str = "",
    default: Optional[str] = None,
    hidden: bool = False,
    choices: Optional[List[str]] = None,
    validator: Optional[Callable[[str], bool]] = None,
    verbose: bool = False
) -> str:
    """
    Get input from the user with various options.

    Args:
        prompt: Text to display when asking for input
        default: Default value if user enters nothing
        hidden: Whether to hide input (for passwords)
        choices: List of valid choices
        validator: Function to validate input
        verbose: Whether to log details

    Returns:
        User input string
    """
    import getpass

    display_prompt = prompt
    if default is not None:
        display_prompt = f"{prompt} [{default}]: "
    elif prompt and not prompt.endswith(': '):
        display_prompt = f"{prompt}: "

    if choices:
        choice_str = '/'.join(choices)
        display_prompt = f"{display_prompt.rstrip(': ')} ({choice_str}): "

    if verbose:
        logger.info(f"Requesting user input: {prompt}")
        if choices:
            logger.debug(f"Available choices: {choices}")

    while True:
        if hidden:
            user_input = getpass.getpass(display_prompt)
        else:
            user_input = input(display_prompt)

        if not user_input and default is not None:
            user_input = default

        if choices and user_input not in choices:
            print(f"Invalid choice. Please choose from: {', '.join(choices)}")
            continue

        if validator and not validator(user_input):
            print("Invalid input. Please try again.")
            continue

        if verbose:
            if hidden:
                logger.debug("Received hidden user input")
            else:
                logger.debug(f"Received user input: {user_input}")

        return user_input

def get_confirmation(
    prompt: str = "Continue?",
    default: bool = True,
    verbose: bool = False
) -> bool:
    """
    Ask the user for yes/no confirmation.

    Args:
        prompt: Question to ask the user
        default: Default answer if user just presses Enter
        verbose: Whether to log details

    Returns:
        True for yes, False for no
    """
    default_str = "Y/n" if default else "y/N"
    prompt_text = f"{prompt} [{default_str}] "

    if verbose:
        logger.info(f"Requesting confirmation: {prompt}")

    while True:
        response = input(prompt_text).strip().lower()

        if not response:
            return default

        if response in ('y', 'yes'):
            return True

        if response in ('n', 'no'):
            return False

        print("Please answer with 'yes' or 'no'")

def find_executable(name: str) -> Optional[str]:
    """
    Find the full path to an executable in the system PATH.

    Args:
        name: Name of the executable to find

    Returns:
        Full path to executable or None if not found
    """
    return shutil.which(name)

def check_command_exists(cmd: str) -> bool:
    """
    Check if a command exists in the system PATH.

    Args:
        cmd: Command name to check

    Returns:
        True if command exists, False otherwise
    """
    return find_executable(cmd) is not None

def setup_signal_handler(
    signal_list: List[signal.Signals] = None,
    handler: Callable[[int, Any], None] = None
) -> None:
    """
    Set up signal handlers for graceful script termination.

    Args:
        signal_list: List of signals to handle (defaults to SIGINT, SIGTERM)
        handler: Function to handle the signal
    """
    if signal_list is None:
        signal_list = [signal.SIGINT, signal.SIGTERM]

    def default_handler(sig, frame):
        """Default handler that exits gracefully."""
        logger.info(f"Received signal {sig}, exiting gracefully")
        sys.exit(0)

    handler = handler or default_handler

    for sig in signal_list:
        signal.signal(sig, handler)
        logger.debug(f"Set up handler for signal {sig}")

def watch_file(
    filename: str,
    callback: Callable[[str], None],
    interval: float = 1.0,
    stop_event=None
) -> None:
    """
    Watch a file for changes and call the callback function with new content.

    Args:
        filename: Path to file to watch
        callback: Function to call with new content
        interval: How often to check for changes (seconds)
        stop_event: Event to signal stopping the watch
    """
    if stop_event is None:
        stop_event = threading.Event()

    logger.info(f"Starting to watch file: {filename}")

    last_size = 0
    if os.path.exists(filename):
        last_size = os.path.getsize(filename)

    while not stop_event.is_set():
        if os.path.exists(filename):
            current_size = os.path.getsize(filename)

            if current_size > last_size:
                with open(filename, 'r') as f:
                    f.seek(last_size)
                    new_content = f.read()
                    callback(new_content)

                last_size = current_size

        time.sleep(interval)

    logger.info(f"Stopped watching file: {filename}")

def get_script_path() -> str:
    """Get the absolute path of the directory containing the current script."""
    return os.path.dirname(os.path.abspath(sys.argv[0]))

def is_root() -> bool:
    """Check if the current user has root/admin privileges."""
    return os.geteuid() == 0 if hasattr(os, 'geteuid') else False

def resource_usage(pid: Optional[int] = None) -> Dict[str, Any]:
    """
    Get resource usage information for a process.

    Args:
        pid: Process ID (current process if None)

    Returns:
        Dictionary of resource usage information
    """
    if pid is None:
        pid = os.getpid()

    try:
        process = shutil.Process(pid)

        info = {}
        info['pid'] = pid
        info['cpu_percent'] = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        info['memory_rss'] = memory_info.rss
        info['memory_vms'] = memory_info.vms
        info['threads'] = len(process.threads())
        info['open_files'] = len(process.open_files())
        info['connections'] = len(process.connections())

        return info
    except (shutil.NoSuchProcess, shutil.AccessDenied):
        return {'error': 'Could not access process information'}

def format_output(
    output: str,
    colorize: bool = True,
    max_lines: Optional[int] = None,
    highlight_pattern: Optional[str] = None
) -> str:
    """
    Format command output for display with optional colorization.

    Args:
        output: Command output string
        colorize: Whether to add ANSI color codes
        max_lines: Maximum number of lines to show
        highlight_pattern: Regex pattern to highlight

    Returns:
        Formatted output string
    """
    lines = output.splitlines()
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines] + [f"... (truncated, {len(lines) - max_lines} more lines)"]

    if colorize:
        RESET = "\033[0m"
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"

        error_pattern = r'(error|exception|failed|failure|traceback|critical)(:|\s)'
        warning_pattern = r'(warning|warn|deprecated)(:|\s)'

        for i, line in enumerate(lines):
            if highlight_pattern:
                line = re.sub(f'({highlight_pattern})', f'{YELLOW}\\1{RESET}', line, flags=re.IGNORECASE)

            line = re.sub(error_pattern, f'{RED}\\1\\2{RESET}', line, flags=re.IGNORECASE)
            line = re.sub(warning_pattern, f'{YELLOW}\\1\\2{RESET}', line, flags=re.IGNORECASE)

            lines[i] = line

    return '\n'.join(lines)
