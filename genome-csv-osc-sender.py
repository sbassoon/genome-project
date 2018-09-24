import argparse
import csv
from typing import List, Any

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client

step_count = 0


def initCSV():
    fileName = "gen-self.csv"

    with open(fileName) as csvfile:
        readCSV = csv.reader(csvfile, delimiter='	')
        row_count = sum(1 for row in csvfile) - 1 #subtract 1 for header
        csvfile.seek(0)

        readCSV.__next__()
        rsids = []
        chromosomes = []
        positions = []
        genotypes = []

        dataArray = []

        for row in readCSV:
            rsid = row[0]
            chromosome = row[1]
            position = row[2]
            genotype = row[3]

            rsids.append(rsid)
            chromosomes.append(chromosome)
            positions.append(position)
            genotypes.append(genotype)

            dataArray.append(rsids)
            dataArray.append(chromosomes)
            dataArray.append(positions)
            dataArray.append(genotypes)

    return fileName, dataArray, row_count


def sendMessage(address, label, data):
    global step_count
    global dataArrayed
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
                        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=1068,
                        help="The port the OSC server is listening on")
    server_args = parser.parse_args()
    client = udp_client.SimpleUDPClient(server_args.ip, server_args.port)

    try:
        if str(address) == "/index/step" and str(data) == "trigger":
            print("Step: " + str(step_count))
            client.send_message("/rsid", str(dataArrayed[0][step_count]))
            client.send_message("/chromosome", str(dataArrayed[1][step_count]))
            client.send_message("/position", float(dataArrayed[2][step_count]))
            client.send_message("/genotype", str(dataArrayed[3][step_count]))
            client.send_message("/list/step-count", float(step_count))
            step_count += 1
        elif str(address) == "/index/set" and type(data) is int:
            print("Set: " + str(step_count))
            client.send_message("/rsid", str(dataArrayed[0][data]))
            client.send_message("/chromosome", str(dataArrayed[1][data]))
            client.send_message("/position", float(dataArrayed[2][data]))
            client.send_message("/genotype", str(dataArrayed[3][data]))
            client.send_message("/list/step-count", float(step_count))
            step_count = data + 1
        elif str(address) == "/index/insert" and type(data) is int:
            print("Insert: Index " + str(data))
            client.send_message("/rsid", str(dataArrayed[0][data]))
            client.send_message("/chromosome", str(dataArrayed[1][data]))
            client.send_message("/position", float(dataArrayed[2][data]))
            client.send_message("/genotype", str(dataArrayed[3][data]))
            client.send_message("/list/step-count", float(step_count))
        elif str(address) == '/list' and str(data) == "init":
            print("List initialized.")
            verify = initCSV()
            dataArrayed = verify[1]
            length = verify[2]
            client.send_message("/list/length", float(length))
            print("File length: " + str(length))
    except IndexError:
        print("List end.")
        client.send_message("/list/end", "bang")
    except FileNotFoundError:
        print("List select: File not found. Check index listing.")
        client.send_message("/list/select", "File not found. Check index listing.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=5008, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map('/index/step', sendMessage, 'Step')
    dispatcher.map('/index/set', sendMessage, 'Set')
    dispatcher.map('/index/insert', sendMessage, 'Insert')
    dispatcher.map('/list', sendMessage, 'List select')

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print(f'Serving on {server.server_address}')
    server.serve_forever()

