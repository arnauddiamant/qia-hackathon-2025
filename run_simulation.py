from application import ClientProgram, ServerProgram

from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

# import network configuration from file
cfg = StackNetworkConfig.from_file("config.yaml")

# Initialize protocol programs
Client_program = ClientProgram()
Server_program = ServerProgram()

# Map each network node to its corresponding protocol program
programs = {"Client": Client_program,
            "Server": Server_program}

# Run the simulation
run(
    config=cfg,
    programs=programs,
    num_times=1,
)
