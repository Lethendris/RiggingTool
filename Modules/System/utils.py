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


def stripLeadingNamespace(nodeName):
    """
    Splits a node name into namespace and base name.

    Args:
        nodeName (str): The full node name potentially with a namespace.

    Returns:
        list[str] or None: [namespace, baseName] if a namespace exists, otherwise None.
    """
    if ':' not in nodeName:
        return None

    namespace, _, baseName = nodeName.partition(':')
    return [namespace, baseName]