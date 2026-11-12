"""Count the words in a text file: python3 wc.py FILE"""
import sys


def count_words(text):
    return len(text.split())


def main(argv):
    if len(argv) != 1:
        print("usage: wc.py FILE", file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        print(count_words(f.read()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
