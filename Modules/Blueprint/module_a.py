import maya.cmds as cmds

MODULE_NAME = "ModuleA"
MODULE_DESCRIPTION = "Module A Description"
MODULE_ICON = "path/to/icon.png"  # Optional

class ModuleA:

    def __init__(self, userSpecifiedName):
        self.moduleName = MODULE_NAME
        self.userSpecifiedName = userSpecifiedName

        self.moduleNameSpace = f'{self.moduleName}__{self.userSpecifiedName}'

        print(self.moduleNameSpace)

    def install(self):
        cmds.namespace(setNamespace = ':')
        cmds.namespace(add = self.moduleNameSpace)
