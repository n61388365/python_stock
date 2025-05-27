import sys
import os
import json
import pythoncom
import win32comext.shell.shell as shell
import win32comext.shell.shellcon as shellcon
from win32comext.propsys import propsys, pscon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon

import ctypes



# File to store recent arguments
HISTORY_FILE = os.path.join(os.path.expanduser("~"), "recent_args.json")
print(HISTORY_FILE)
# Application ID for Jump List
APP_ID = "MyPythonApp"

def load_recent_args():
    """Load recent arguments from JSON file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_arg(arg):
    """Save argument to recent args list."""
    recent_args = load_recent_args()
    if arg in recent_args:
        recent_args.remove(arg)
    recent_args.insert(0, arg)
    recent_args = recent_args[:10]  # Limit to 10 arguments
    with open(HISTORY_FILE, 'w') as f:
        json.dump(recent_args, f)
    return recent_args

def update_jump_list(recent_args):
    """Update Jump List with recent arguments using win32com.shell."""
    # pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    pythoncom.CoInitialize()
    collection = pythoncom.CoCreateInstance(
            shell.CLSID_EnumerableObjectCollection,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IObjectCollection)
        # Create ICustomDestinationList

    dest_list = pythoncom.CoCreateInstance(
        shell.CLSID_DestinationList,
        None,
        pythoncom.CLSCTX_INPROC_SERVER,
        shell.IID_ICustomDestinationList
    )
    dest_list.SetAppID("company.app.1")
    num_items, shell_items = dest_list.BeginList()
    print(f"BeginList {num_items} succeeded: Fetched={shell_items.GetCount()}")
    print(dest_list)

    exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
    for arg in recent_args:
        print("param:", arg)
        # Create IShellLink for the task
        link = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink
        )
        link.SetPath(exe_path)
        link.SetArguments(arg)  # Pass argument to EXE
        link.SetDescription(f"Run with {arg}")
        link.SetShowCmd(1)  # SW_SHOWNORMAL
        # Use EXE's icon
        link.SetIconLocation(exe_path, 0)

        # Set PKEY_AppUserModel_ID
        try:
            prop_store = link.QueryInterface(propsys.IID_IPropertyStore)
            print(pscon.PKEY_AppUserModel_ID)
            prop_store.SetValue(pscon.PKEY_Title, propsys.PROPVARIANTType(f"股票 {arg}", pythoncom.VT_BSTR))
            prop_store.SetValue(pscon.PKEY_AppUserModel_ID, propsys.PROPVARIANTType("company.app.1"))
            prop_store.Commit()
        except Exception as e:
            print(f"Warning: Failed to set PKEY_Title for arg '{arg}': {e}")

        # Add to Jump List tasks
        collection.AddObject(link)
    dest_list.AppendCategory("Recent", collection)

    # array = collection.QueryInterface(shell.IID_IObjectArray)
    # print("array count:", array.GetCount())
    # print("collection count:", array.GetCount())

    # hresult = dest_list.AddUserTasks(array)
    # print("AddUserTasks:", hresult)

    # Commit the Jump List
    response = dest_list.CommitList()
    print("CommitList", response)
    pythoncom.CoUninitialize()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Nuitka 示例")
        # self.setWindowIcon(QIcon(".\stock.ico"))
        self.int_ui()
    
    def int_ui(self):
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.label = QLabel(f"{sys.argv}")
        main_layout.addWidget(self.label)


def main():
    """Main function to handle argument and update Jump List."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_ID)
    app.setWindowIcon(QIcon("stock.ico"))  # Set app icon
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('company.app.1')
    # Get command-line argument
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg:
        update_jump_list([arg])

    window = MainWindow()
    window.show()

    # if arg:
    #     # Save the argument and attempt to update Jump List
    #     recent_args = save_arg(arg)
    #     update_jump_list(recent_args)
    #     print(f"Executing with argument: {arg}")
    #     # Add your logic here (e.g., process the argument)
    # else:
    #     # If no argument, load existing Jump List
    #     recent_args = load_recent_args()
    #     if recent_args:
    #         update_jump_list(recent_args)
    #     print("No argument provided. Recent arguments may be available in the Jump List.")

    # Keep the app running for testing
    sys.exit(app.exec())

if __name__ == "__main__":
    main()