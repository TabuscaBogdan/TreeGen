bl_info = {
    "name": "Realistic Trees Addon",
    "description": "",
    "author": "Tabusca Bogdan",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy
# ============= Proprieties =================
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty)
from bpy.types import Panel, Operator, PropertyGroup


class TreeGeneralProprieties(PropertyGroup):
    nrCircleVertices: IntProperty(
        name="Nr of Circle Verices",
        description="How detailed the Tree will be",
        default = 30,
        min=3,
        max=360
    )
    precision: IntProperty(
        name="Precision of Calculus",
        description="How precise will the calculations be.",
        default=2,
        min=1,
        max=6
    )
    circleRay: FloatProperty(
        name="Circle ray.",
        description="How wide will the tree be.",
        default=3,
        min=1,
        max=10
    )
    stumpAbruptness: FloatProperty(
        name="Abruptness of the Stump.",
        description="How tall will the tree's base be.",
        default=3,
        min=1,
        max=10
    )

class TreeBarkProperties(PropertyGroup):
    barkDeformities: BoolProperty(
        name="Enable Bark Deformities",
        description="If Enabled the trunk and branches will have deformities on its surface",
        default=False
    )
    barkMutationChance: FloatProperty(
        name="Bark Mutation Chance",
        description="Chance for bark to mutate",
        default=1.0,
        min=-100.0,
        max=100
    )
    barkMutationFactor:  IntProperty(
        name="Bark Mutation Factor",
        description="Lower Factor = more noticeable mutations",
        default=1,
        min=1,
        max=10
    )
    barkMaterialName: StringProperty(
        name="Bark Material Name (!)",
        description="The Name of the Material you want to apply to the tree's bark",
        default="Default",
        maxlen=1024,
    )

class TreeLeavesProperties(PropertyGroup):
    leavesPerBranchInferiorLimit: IntProperty(
        name="Minimum Number of Leaves Per Branch",
        description="How many Leaves will certainly be on a Branch",
        default=5,
        min=0,
        max=50,
    )
    leavesPerBranchSuperiorLimit: IntProperty(
        name="Maximum Number of Leaves Per Branch",
        description="How many Leaves can maximum be on a Branch",
        default=10,
        min=0,
        max=80,
    )
    leavesDistance: IntProperty(
        name="Leaves Distance",
        description="greater number = smaller distance between leaves",
        default=1,
        min=1,
        max=10,
    )
    leafRotationAngleDeviationFactor: IntProperty(
        name="Leaf Rotation Angle",
        description="+- [0,LeafRA] when placed on a branch",
        default=30,
        min=0,
        max=180,
    )
    leafObjectName: StringProperty(
        name="Leaf Object Name (!)",
        description="The Object that will be placed as a leaf (MUST EXIST!)",
        default="Leaf",
        maxlen=1024,
    )

class TreeBranchingProperties(PropertyGroup):
    startingSplitChance: IntProperty(
        name="Starting Split Chance",
        description="Initial chance to split",
        default=10,
        min=0,
        max=100
    )
    splitChanceGain: FloatProperty(
        name="Split Chance Gain",
        description="Gain Per Step:",
        default=1.0,
        min=-100.0,
        max=100
    )
    splitIntervalMinim: IntProperty(
        name="Minimum Branch Number",
        description="How many Branches will sprout when split",
        default=2,
        min=2,
        max=10
    )
    splitIntervalMaxim: IntProperty(
        name="Maximum Branch Number",
        description="How many Branches will sprout when split",
        default=3,
        min=2,
        max=20
    )

    angleIntervalDiv: IntProperty(
        name="Angle Interval Division Factor",
        description="PI/DivFactor (How wide can it grow)",
        default=5,
        min=2,
        max=180
    )

    maxBranchingAngleDeviationDiv: FloatProperty(
        name="Branch Max Twist Factor",
        description="PI/DivFactor (Maximum Branch Twist):",
        default=1.2,
        min=0.5,
        max=10
    )

    rayReductionPrecentPerStep: IntProperty(
        name="Ray Precent Reduction Per Step",
        description="Loss per Step",
        default=2,
        min=1,
        max=100
    )
    stopCircleRayPrecent: IntProperty(
        name="Ray Precent Stop Point",
        description="At which point branch growth will stop",
        default=30,
        min=0,
        max=99
    )

class TreeCreationPannel(Panel):
    bl_idname = "OBJECT_PT_TreeCreationPannelId"
    bl_label = "Tree Proprieties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TB Tree Creation"
    bl_context = "objectmode"

    @classmethod
    def poll(self, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene

class TreeGeneralPropertiesPanel(TreeCreationPannel, Panel):
    bl_idname = "OBJECT_PT_TreeGeneralPropertiesPanelId"
    bl_label = "General Properties"
    bl_parent_id = "OBJECT_PT_TreeCreationPannelId"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This section controls "
                          "cylinder circles properties "
                          "from witch the tree "
                          "is made of.")
        scene = context.scene
        treeTool = scene.treeToolGeneral

        layout.prop(treeTool, "nrCircleVertices")
        layout.prop(treeTool, "circleRay")
        layout.prop(treeTool, "stumpAbruptness")
        layout.prop(treeTool, "precision")

class TreeBarkPropertiesPanel(TreeCreationPannel, Panel):
    bl_idname = "OBJECT_PT_TreeBarkPropertiesPanelId"
    bl_label = "Bark Properties"
    bl_parent_id = "OBJECT_PT_TreeCreationPannelId"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This section controls the tree's bark")
        scene = context.scene
        treeTool = scene.treeToolBark

        layout.prop(treeTool, "barkDeformities")
        layout.prop(treeTool, "barkMutationChance")
        layout.prop(treeTool, "barkMutationFactor")
        layout.prop(treeTool, "barkMaterialName")

class TreeLeavesPropertiesPanel(TreeCreationPannel, Panel):
    bl_idname = "OBJECT_PT_TreeLeavesPropertiesPanelId"
    bl_label = "Leaves Properties"
    bl_parent_id = "OBJECT_PT_TreeCreationPannelId"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This section controls the tree's leaves")
        scene = context.scene
        treeTool = scene.treeToolLeaves

        layout.prop(treeTool, "leavesPerBranchInferiorLimit")
        layout.prop(treeTool, "leavesPerBranchSuperiorLimit")
        layout.prop(treeTool, "leavesDistance")
        layout.prop(treeTool, "leafRotationAngleDeviationFactor")
        layout.prop(treeTool, "leafObjectName")

class TreeBranchingPropertiesPanel(TreeCreationPannel, Panel):
    bl_idname = "OBJECT_PT_TreeBranchingPropertiesPanelId"
    bl_label = "Branching Properties"
    bl_parent_id = "OBJECT_PT_TreeCreationPannelId"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This section controls "
                          "the branching of the tree.")
        scene = context.scene
        treeTool = scene.treeToolBranching

        layout.prop(treeTool, "startingSplitChance")
        layout.prop(treeTool, "splitChanceGain")
        layout.prop(treeTool, "splitIntervalMinim")
        layout.prop(treeTool, "splitIntervalMaxim")
        layout.prop(treeTool, "angleIntervalDiv")
        layout.prop(treeTool, "maxBranchingAngleDeviationDiv")
        layout.prop(treeTool, "rayReductionPrecentPerStep")
        layout.prop(treeTool, "stopCircleRayPrecent")

class TreeCreationButtonPanel(TreeCreationPannel,Panel):
    bl_idname = "OBJECT_PT_TreeCreationButtonPanelId"
    bl_label = "Branching Properties"
    bl_parent_id = "OBJECT_PT_TreeCreationPannelId"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="After Setting the Properties and Most Importantly,"
                          "specifing the Leaf object and bark material, "
                          "click to generate the tree")
        scene = context.scene
        treeTool = scene.treeToolGeneral

        layout.operator("wm.create_tree")

class CreateTree(Operator):
    bl_idname = "wm.create_tree"
    bl_label = "Create Tree"

    def execute(self, context):
        scene = context.scene
        treeTool = scene.treeToolGeneral

        print("I work!")
        print("bool state:", treeTool.barkDeformities)

        return {'FINISHED'}

#======== Class Registration ====================
classes = (
    TreeGeneralProprieties,
    TreeBarkProperties,
    TreeBranchingProperties,
    TreeLeavesProperties,
    TreeCreationPannel,
    TreeGeneralPropertiesPanel,
    TreeBarkPropertiesPanel,
    TreeBranchingPropertiesPanel,
    TreeLeavesPropertiesPanel,
    TreeCreationButtonPanel,
    CreateTree
)
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    # ============== Important!(register properties)==
    bpy.types.Scene.treeToolGeneral = PointerProperty(type=TreeGeneralProprieties)
    bpy.types.Scene.treeToolBranching = PointerProperty(type=TreeBranchingProperties)
    bpy.types.Scene.treeToolBark = PointerProperty(type=TreeBarkProperties)
    bpy.types.Scene.treeToolLeaves = PointerProperty(type=TreeLeavesProperties)
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.treeToolGeneral
    del bpy.types.Scene.treeToolBranching
    del bpy.types.Scene.treeToolBark
    del bpy.types.Scene.treeToolLeaves

if __name__ == "__main__":
    register()

