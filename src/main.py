from sys import argv, exit
from inp import get_inp_file
from gmh import gmh

if __name__ == '__main__':
    if len(argv) != 4:
        print('Error: expecting three arguments: {0} input-file d1 d2'
              .format(argv[0]))
        exit(1)

    inp_file = ''
    try:
        inp_file = get_inp_file(argv[1])
    except FileNotFoundError:
        print("Error: input file '{0}' has not been found.".format(argv[1]))
        exit(1)

    print("Input file '{0}' has been found.".format(inp_file))

    gmh(inp_file, int(argv[2]), int(argv[3]), argv[1])

    exit(0)
