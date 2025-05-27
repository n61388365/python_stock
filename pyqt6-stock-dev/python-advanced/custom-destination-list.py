import sys
import pythoncom
import win32comext.shell.shell as shell
from win32comext.propsys import propsys, pscon


aumid = "Pyptom.Test.RealtimeBidFollowup"  # Replace with your desired AUMID


def demo():
    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    dest_list = pythoncom.CoCreateInstance(
        shell.CLSID_DestinationList,
        None,
        pythoncom.CLSCTX_INPROC_SERVER,
        shell.IID_ICustomDestinationList
    )
    dest_list.SetAppID(aumid)
    punk, cFetched = dest_list.BeginList()
    print(f"BeginList succeeded: cFetched={cFetched}")

    collection = pythoncom.CoCreateInstance(
            shell.CLSID_EnumerableObjectCollection,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IObjectCollection)

    link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink,
        None,
        pythoncom.CLSCTX_INPROC_SERVER,
        shell.IID_IShellLink
    )

    exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
    link.SetPath(exe_path)
    link.SetArguments('000750')  # Pass argument to EXE
    link.SetDescription(f"Run with 000750")
    link.SetShowCmd(1)  # SW_SHOWNORMAL
    # Use EXE's icon
    link.SetIconLocation(exe_path, 0)

    # Load the shortcut as an IShellLink COM object
    punk = link.QueryInterface(shell.IID_IShellLink)
    property_store = punk.QueryInterface(propsys.IID_IPropertyStore)
    
    # Set the System.AppUserModel.ID property

    prop_key = propsys.PSGetPropertyKeyFromName("System.AppUserModel.ID")
    print("key:", prop_key, pscon.PKEY_AppUserModel_ID)
    prop_value = propsys.PROPVARIANTType(aumid, pythoncom.VT_BSTR)
    # prop_value.set_string(aumid)
    property_store.SetValue(prop_key, prop_value)
    property_store.SetValue(pscon.PKEY_Title, propsys.PROPVARIANTType("I am here"))
    
    # Commit the changes
    property_store.Commit()

    # Add to Jump List tasks
    collection.AddObject(link)

    array = collection.QueryInterface(shell.IID_IObjectArray)
    print(collection.GetCount())
    dest_list.AppendCategory("股票", collection)
    dest_list.AddUserTasks(array)

    # Commit the Jump List
    dest_list.CommitList()

    dest_list.DeleteList()

    pythoncom.CoUninitialize()


if __name__ == '__main__':
    demo()
