import maya.cmds as cmds
import numpy as np
from matrix_rig.core import Component, Guide
from matrix_rig.utils import calculateLocalOffset, numpyToMayaList


class SpineComponent(Component):
    """A simple FK/IK spline spine component."""

    def __init__(self, name: str, guide_data: List[Guide], parent: Component):
        # Must call super and pass the parent reference
        super().__init__(name = name, guide_data = guide_data, parent = parent)

        # Internal Storage (We know we need controls and joints)
        self.controls = []
        self.deform_joints = []
        self.num_joints = 5  # Example fixed joint count

    def build(self):
        # 1. VALIDATION: Check for required guides
        if len(self.guide_data) != 3:
            raise ValueError("SpineComponent requires exactly 3 Guide locators (start, mid, end).")

        # 2. GET PARENT MATRIX INPUT: The attribute we will connect to
        # Example: parent is RootComponent, output is 'deform_matrix' (from root.py)
        self.parent_matrix_attr = self.parent.outputs["deform_matrix"]

        # 3. GET GUIDE MATRICES: Extract W matrices from guides
        start_guide = self.guide_data[0]  # The 'start' guide
        end_guide = self.guide_data[2]  # The 'end' guide

        start_W = start_guide.getWorldMatrix()
        end_W = end_guide.getWorldMatrix()

        # Extract translation vectors (Position is in the 4th column, rows 0, 1, 2)
        P_start = start_W[:3, 3]
        P_end = end_W[:3, 3]

        # 4. CREATE CONTROLS & CALCULATE LOCAL OFFSETS

        # A. Start Control (e.g., Hip Control)
        hip_ctrl = cmds.circle(name = f"{self.name}_hip_CTRL", ch = False)[0]

        # B. CALCULATE OFFSET: This is the core matrix step!
        # M_Local = W_Parent_Inverse * W_Child (W_Child is the guide's W)
        parent_W = self.parent.getOutputMatrix(self.parent_matrix_attr)  # Utility function to get W_Parent
        hip_local_offset_M = calculateLocalOffset(start_W, parent_W)

        # C. APPLY OFFSET: We apply the local offset matrix directly to the control's transform
        cmds.xform(hip_ctrl, matrix = numpyToMayaList(hip_local_offset_M), os = True)

        # Store the control for connection
        self.output_nodes["hip_control"] = hip_ctrl
        self.outputs["hip_matrix"] = f"{hip_ctrl}.worldMatrix[0]"

        # 5. CREATE SPINE JOINT CHAIN (Placeholder for more complex spline IK later)
        # Create N interpolation factors (0.0 to 1.0, including start and end)
        # We need N joints, so we create N points, with N-1 segments.
        factors = np.linspace(0.0, 1.0, self.num_joints)

        prev_joint = None

        for i, t in enumerate(factors):
            # Calculate the interpolated position vector (P_i)
            P_i = (1 - t) * P_start + t * P_end

            # Create the joint
            jnt_name = f"{self.name}_{i:02d}_JNT"

            # Position the joint at the interpolated coordinates
            # Note: We create the joint without a parent initially, then reparent later.
            deform_joint = cmds.joint(
                name = jnt_name,
                position = P_i.tolist(),
                absolute = True  # Use absolute/world space coordinates
            )

            # Reparent the joint to the previous one to form a chain
            if prev_joint:
                cmds.parent(deform_joint, prev_joint)

            self.deform_joints.append(deform_joint)
            prev_joint = deform_joint

            # Store the joint for later use
            self.output_nodes[f"joint_{i:02d}"] = deform_joint

        # Ensure the joint chain is parented under a root rig group (e.g., Root_rig_GRP)
        # For simplicity now, we'll assume the Root Component's primary group is available.
        # This will be refined in the Rig class that orchestrates the build.

    def connect(self):
        # 1. CONNECT CONTROLS TO PARENT: This creates the matrix constraint.
        # We connect the Root's deform joint W to our Hip Control's PIM.

        hip_ctrl = self.output_nodes["hip_control"]

        # Root's deform joint worldMatrix[0] is the driving matrix
        parent_driver_attr = self.parent_matrix_attr

        # We connect the driver's W to the control's PIM (Parent Inverse Matrix)
        # This tells Maya how the control moves relative to the parent.
        cmds.connectAttr(parent_driver_attr, f"{hip_ctrl}.parentInverseMatrix[0]")

        # 2. CONNECT JOINTS TO CONTROLS (Placeholder for future complexity)
        # ... The spine joints will be driven by the hip and chest controls via a blend or spline ...
        pass