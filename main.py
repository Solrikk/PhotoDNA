import logging
from gui import create_gui

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    create_gui()

if __name__ == "__main__":
    main()
