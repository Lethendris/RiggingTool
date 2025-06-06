import maya.cmds as cmds

def findHighestTrailingNumber(names, baseName):
    highestValue = 0

    for name in names:
        if name.startswith(baseName):
            suffix = name[len(baseName):]
            if suffix.isdigit():
                highestValue = max(highestValue, int(suffix))

    return highestValue

def addHierarchyToSet(rootObject, setName):
    # Get all descendants including the root
    hierarchy = cmds.listRelatives(rootObject, allDescendents=True, fullPath=True) or []
    hierarchy.append(rootObject)  # include the root itself

    # Create or add to the set
    if not cmds.objExists(setName):
        cmds.sets(hierarchy, name=setName)
    else:
        cmds.sets(hierarchy, edit=True, add=setName)
