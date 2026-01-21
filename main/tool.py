# Entry point for Amazon Buy Box Analyzer GUI
# Initializes the Tool class and runs the Tkinter main loop

from tools.tool import Tool


def main():
    """
    Main function to launch the Buy Box Analyzer GUI.
    """
    tool = Tool("tool/tool.log")
    try:
        tool.run()
    finally:
        tool.dispose()


if __name__ == "__main__":
    main()
