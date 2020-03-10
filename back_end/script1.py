import sys


def hello():
    print("ciao")
    sys.stdout.flush()
    f = open("test.txt", "w+")
    f.write("ciao")
    f.close()
    return


hello()
