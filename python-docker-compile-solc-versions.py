#!/usr/local/bin/python

import os
import sys
import subprocess
from sys import argv, exit

import re
from termcolor import colored

# Troca a versão do solidity no arquivo do contrato.
def change_version_contract_code(contract_file_base, comp_version_number):
    #open text file in read mode
    source_code = open(contract_file_base, "r")
    
    #read whole file to a string
    data = source_code.read()
     
    #close file
    source_code.close()

    #print(data)
    data = re.sub(r'pragma solidity [0-9]+.[0-9]+.[0-9]+;', "pragma solidity {};".format(comp_version_number), data)
    # print(data)

    return data


if __name__ == "__main__":
    if(len(sys.argv) < 2):
        raise TypeError("Use: python pytho-docker-compile-solc-versions.py ContractFile.sol")

    aux = argv[1].split('.')
    if aux[-1] != 'sol':
      raise IOError(argv[1] + " is not a .sol file")
    elif not os.path.exists(argv[1]):
        raise IOError(argv[1] + " not exists.")
    else:
        file_contract_template = argv[1]

        print(colored("Compiling {}...".format(file_contract_template),'green'))
        
        file_solc_versions = open("solc-versions-uniq.txt", "r")

        evm_versions_list = ["shanghai", "paris", "london", "berlin", "istambul", "petersburg", "constantinople", "byzantium", "spuriousDragon", "tangerineWhistle", "homestead"]

        for comp_version in file_solc_versions.readlines():
            # Change the solidity version in source code.
            # pragma solidity ^{comp_version};
            version_number = comp_version.split("+")
            versioned_contract = change_version_contract_code(file_contract_template, version_number[0])

            # Create a specific contract file with correct solc version.
            contract_file = "{}-solidity-{}.sol".format(file_contract_template.split(".")[0], version_number[0])
            print(colored("Creating {} file with correct solidity version {}.".format(contract_file, version_number[0]),'blue'))

            f = open(contract_file, "w")
            f.write(versioned_contract)
            f.close()
            
            for evm_version in evm_versions_list:
                print(colored("  Compiling {} with solc-{} for EVM {}.".format(contract_file, version_number[0], evm_version), 'green'))


                path = subprocess.run(["pwd"], stdout=subprocess.PIPE)
                path = path.stdout.decode('utf-8').strip()

                # command = ["docker", "run", "-v", "{}:{}".format(path,path), "-w", "{}".format(path), "{}".format(solc_version), "-o", "{}/output".format(path), "--abi", "--bin", "--gas", "{}/{}".format(path, contract_file)]
                # sudo docker  run  -v $(pwd):$(pwd) -w $(pwd) -i ethereum/solc:0.8.21 --evm-version shanghai Contrato.sol --combined-json abi,asm,bin,opcodes,gas > Contrato.sol.json
                command = ["docker", "run", "-v", "{}:{}".format(path,path), "-w", "{}".format(path), "ethereum/solc:{}".format(version_number[0]), "--evm-version", "{}".format(evm_version), "--abi", "--bin", "--gas", "--opcodes", "{}/{}".format(path, contract_file)]
                
                print(colored('  Running the command:', 'red'), colored(command, 'white'))
                # print("  Running the command: ", command)
                # Run the solc on docker.
                # sudo docker run -v ./:/sources ethereum/solc:0.8.21 -o /sources/output --abi --bin --gas /sources/Contrato.sol
                # sudo docker  run  -v $(pwd):$(pwd) -w $(pwd) -i ethereum/solc:0.8.21 --abi --gas --bin -o output Contrato.sol
                # sudo docker  run  -v $(pwd):$(pwd) -w $(pwd) -i ethereum/solc:0.8.21 --abi --gas --bin --opcodes Contrato.sol --machine shanghai
                # result = subprocess.run(command, capture_output=True, text=True)
                # sudo docker  run  -v $(pwd):$(pwd) -w $(pwd) -i ethereum/solc:0.8.21 Contrato.sol --combined-json abi,asm,ast,bin,bin-runtime,devdoc,opcodes > Contrato.sol.json
                # sudo docker  run  -v $(pwd):$(pwd) -w $(pwd) -i ethereum/solc:0.8.21 --evm-version shanghai Contrato.sol --combined-json abi,asm,ast,bin,bin-runtime,devdoc,opcodes > Contrato.sol.json
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                print("  " + result.stdout.decode('utf-8'))

                # Create output directory and files.
                if not os.path.exists(os.path.join(os.getcwd(), 'output')):
                    os.makedirs('output')

                output_file = open(os.path.join(os.getcwd(), 'output', "{}-solc-{}-evm-version-{}-abi-bin-gas-opcodes-out.txt".format(contract_file, version_number[0], evm_version)), 'w')
                error_file = open(os.path.join(os.getcwd(), 'output', "{}-solc-{}-evm-version-{}-abi-bin-gas-opcodes-error.txt".format(contract_file, version_number[0], evm_version)), 'w')
                
                output_file.write(result.stdout.decode('utf-8'))
                error_file.write(result.stderr.decode('utf-8'))
                
                output_file.close()
                error_file.close()
            # End of loops evm versions.

            # Remove the generated contract file.
            print(colored("Removing {} file.\n".format(contract_file),'red'))
            
            if os.path.exists(contract_file):
                os.remove(contract_file)
            else:
                print(colored("The file {} does not exist".format(contract_file), 'red'))
        
        print(colored("End of Test Execution.",'green'))

