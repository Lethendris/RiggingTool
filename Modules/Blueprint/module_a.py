MODULE_NAME = "ModuleA"
MODULE_DESCRIPTION = "Module A Description"
MODULE_ICON = "path/to/icon.png"  # Optional

class ModuleA:
    def __init__(self):
        print('we are in module A')

    def install(self):
        print(f'Install {MODULE_NAME}')
