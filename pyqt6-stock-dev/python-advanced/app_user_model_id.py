# windows application
# https://learn.microsoft.com/en-us/windows/win32/shell/appids
# 2025-05-18 Sunday

# How to Form an Application-Defined AppUserModelID
#  An application must provide its AppUserModelID in the following form. 
#  It can have no more than 128 characters and cannot contain spaces. Each section should be pascal-cased.
#  CompanyName.ProductName.SubProduct.VersionInformation
#    CompanyName and ProductName should always be used, 
#  while the SubProduct and VersionInformation portions 
#  are optional and depend on the application's requirements. 
#    SubProduct allows a main application that consists of 
#  several subapplications to provide a separate taskbar 
#  button for each subapplication and its associated windows. 
#    VersionInformation allows two versions of an application
#   to coexist while being seen as discrete entities. If an 
#  application is not intended to be used in that way, 
#  the VersionInformation should be omitted so that an upgraded 
#  version can use the same AppUserModelID as the version that it replaced.

import pythoncom
import win32comext.propsys
from win32comext.propsys import propsys

ps = propsys.SHGetPropertyStoreForWindow(hwnd, propsys.IID_IPropertyStore)
pk = propsys.PSGetPropertyKeyFromName('System.AppUserModel.ID')
pv = propsys.PROPVARIANTType("group_name", pythoncom.VT_BSTR)
ps.SetValue(pk,pv)
ps.Commit()