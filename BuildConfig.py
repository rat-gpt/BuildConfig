import os
import re
import sys
import glob
import subprocess

def replace_define(header_file):
    # Read the file contents
    with open(header_file, 'r') as file:
        content = file.readlines()

    # Pattern to match #define statements (e.g., #define VAR_NAME value)
    define_pattern = re.compile(r'#define\s+(\w+)\s+(\S+)')

    # Dictionary to store variable names and values
    defines = {}

    # Scan the file to find all #define variables
    for line in content:
        match = define_pattern.match(line)
        if match:
            var_name = match.group(1)
            var_value = match.group(2)
            defines[var_name] = var_value

    # Prompt the user to update values for each variable
    for var_name, var_value in defines.items():
        new_value = input(f"Current value of {var_name} is {var_value}. Enter new value (or press Enter to keep the current value): ")
        if new_value:
            defines[var_name] = new_value

    # Modify the specific #define lines with updated values
    modified_content = []
    for line in content:
        modified_line = line
        match = define_pattern.match(line)
        if match:
            var_name = match.group(1)
            if var_name in defines:
                modified_line = define_pattern.sub(f'#define {var_name} {defines[var_name]}', line)
        modified_content.append(modified_line)

    # Write the modified content back to the file
    with open(header_file, 'w') as file:
        file.writelines(modified_content)


def run_msbuild(vcxproj_file):

    print(f"[debug] {vcxproj_file=}")
    # Define the MSBuild command
    msbuild_command = [
        'msbuild', 
        vcxproj_file, 
        '/t:Clean,Build', 
        '/p:Configuration=Release',
		'/p:Platform=x64',
		'/p:OutDir=.\\Build\\Release\\'
    ]

    try:
        # Run the MSBuild command using subprocess
        result = subprocess.run(msbuild_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Print the output
        print("MSBuild Output:\n", result.stdout)

    except subprocess.CalledProcessError as e:
        # Handle errors in case MSBuild fails
        print("MSBuild failed with the following error:\n", e.stderr)
        print("Return code:", e.returncode)



def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path>")
        sys.exit(1)

    # Get the directory path from the argument
    directory_path = sys.argv[1]

    # Search for the BuildConfig.h file in the specified directory
    header_file = os.path.join(directory_path, 'BuildConfig.h')
    

    # Check if the header file exists
    if os.path.isfile(header_file):
        print(f"Found BuildConfig.h in {directory_path}")
        replace_define(header_file)
    else:
        print("BuildConfig.h not found in the specified path.")

    # Check if the vcxproj file exists
    # Use glob to find files matching the *.vcxproj pattern
    search_pattern = os.path.join(directory_path, "*.vcxproj")
    vcxproj_files = glob.glob(search_pattern)

    # Check if there is exactly one .vcxproj file
    if len(vcxproj_files) == 1:
        vcxproj_file = vcxproj_files[0]
        print(f"Found project file: {vcxproj_file}")
        run_msbuild(vcxproj_file)
    else:
        print(f"[-] Found none or multiple vcxproj files. Aborting.")
        exit()

		

if __name__ == "__main__":
    main()
