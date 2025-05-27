import win32com.client
from win32comext.propsys import propsys
from win32comext.shell import shell

def create_shortcut_with_aumid(target_path, shortcut_path, aumid, description=""):
    """
    Create or modify a Windows shortcut (.lnk) and set its AppUserModelID.
    
    Args:
        target_path (str): Path to the target executable (e.g., 'C:\\Program Files\\MyApp\\app.exe')
        shortcut_path (str): Path where the .lnk file will be saved (e.g., 'C:\\Users\\User\\Desktop\\MyApp.lnk')
        aumid (str): The AppUserModelID to set (e.g., 'Company.MyApp')
        description (str): Optional description for the shortcut
    """
    # Create an IShellLink object
    shell_link = win32com.client.Dispatch("WScript.Shell").CreateShortCut(shortcut_path)
    
    # Set basic shortcut properties
    shell_link.TargetPath = target_path
    shell_link.Description = description
    
    # Save the shortcut to disk to get a valid IShellLink
    shell_link.Save()
    
    # Load the shortcut as an IShellLink COM object
    punk = shell_link._oleobj_.QueryInterface(shell.IID_IShellLink)
    property_store = punk.QueryInterface(propsys.IID_IPropertyStore)
    
    # Set the System.AppUserModel.ID property
    prop_key = propsys.PSGetPropertyKeyFromName("System.AppUserModel.ID")
    prop_value = propsys.PROPVARIANT()
    prop_value.set_string(aumid)
    property_store.SetValue(prop_key, prop_value)
    
    # Commit the changes
    property_store.Commit()

# Example usage
if __name__ == "__main__":
    # Example parameters
    target = r"C:\\Program Files\\MyApp\\myapp.exe"  # Replace with your app's executable path
    shortcut = r"C:\\Users\\YourUser\\Desktop\\MyApp.lnk"  # Replace with desired shortcut path
    aumid = "Pyptom.Stock.RealtimeBidFollowup"  # Replace with your desired AUMID
    
    create_shortcut_with_aumid(target, shortcut, aumid, description="My Application Shortcut")
    print(f"Shortcut created at {shortcut} with AUMID {aumid}")