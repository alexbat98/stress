from __future__ import print_function
from random import randint
import sys


mode = randint(0, 6)

if mode == 0:
    print("Success")
elif mode == 1:
    print("PASSED")
elif mode == 2:
    sys.exit(1)
elif mode == 3:
    print("Failed")
elif mode == 4:
    print("Fail")
    sys.exit(10)
elif mode == 5:
    sys.exit(8)
elif mode == 6:
    print("Fail", file=sys.stderr)
