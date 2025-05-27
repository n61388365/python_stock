#######################################################################
# 2025-04-27 周日
# https://pypi.org/project/Nuitka/#tutorial-setup-and-build-on-windows
# to build run:
#    python -m nuitka hello.py --onefile --standalone


def talk(message):
    return "Talk " + message


def main():
    print(talk("Hello World"))


if __name__ == "__main__":
    main()
