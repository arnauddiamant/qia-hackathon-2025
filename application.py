from netqasm.sdk.classical_communication.socket import Socket
from netqasm.sdk.connection import BaseNetQASMConnection
from netqasm.sdk.epr_socket import EPRSocket
from netqasm.sdk.qubit import Qubit

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta


class ClientProgram(Program):
    NODE_NAME = "Client"
    PEER_Server = "Server"

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name=f"program_{self.NODE_NAME}",
            csockets=[self.PEER_Server],
            epr_sockets=[self.PEER_Server],
            max_qubits=2,
        )


    def run(self, context: ProgramContext):
        # get classical sockets
        csocket_Server = context.csockets[self.PEER_Server]
        # get EPR sockets
        epr_socket_Server = context.epr_sockets[self.PEER_Server]
        # get connection to QNPU
        connection = context.connection

        def sendQubit(q):
            # Register a request to create an EPR pair, then apply a Hadamard gate on the epr qubit and measure
            epr_qubit = epr_socket_Server.create_keep()[0]
            q.cnot(epr_qubit)
            q.H()

            # Send result
            epr_res = epr_qubit.measure()
            q_res = q.measure()
            yield from connection.flush()

            csocket_Server.send(f"{epr_res}{q_res}")

        q = Qubit(connection)
        q.H()

        yield from sendQubit(q)


        return {}


class ServerProgram(Program):
    NODE_NAME = "Server"
    PEER_Client = "Client"

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name=f"program_{self.NODE_NAME}",
            csockets=[self.PEER_Client],
            epr_sockets=[self.PEER_Client],
            max_qubits=2,
        )


    def run(self, context: ProgramContext):
        # get classical sockets
        csocket_Client = context.csockets[self.PEER_Client]
        # get EPR sockets
        epr_socket_Client = context.epr_sockets[self.PEER_Client]
        # get connection to QNPU
        connection = context.connection

        def receiveQubit() -> Qubit:
            epr_qubit = epr_socket_Client.recv_keep()[0]
            yield from connection.flush() # wait the measurement

            # receive result
            res = yield from csocket_Client.recv()
            print(res)
            if res[0] == "1":
                epr_qubit.X()
            if res[1] == "1":
                epr_qubit.Z()
            
            return epr_qubit

        q = yield from receiveQubit()

        r = q.measure()
        yield from connection.flush()
        print(f"Bob measured: {r}")

        return {}
