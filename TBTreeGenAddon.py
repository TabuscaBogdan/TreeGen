bl_info = {
    "name": "Add-on Template",
    "description": "",
    "author": "p2or",
    "version": (0, 0, 3),
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


class TreeBranchingProprieties(PropertyGroup):
    barkDeformities: BoolProperty(
        name="Enable or Disable",
        description="A bool property",
        default=False
    )
    startingSplitChance: IntProperty(
        name="Starting Split Chance",
        description="Split Chance Add Up",
        default=10,
        min=0,
        max=100
    )
    splitChanceGain: FloatProperty(
        name="Set a value",
        description="A integer property",
        default=1.0,
        min=-100.0,
        max=100
    )


class TreeCreationPannel(Panel):
    bl_idname = "OBJECT_PT_TreeCreationPannelId"
    bl_label = "Tree Proprieties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        treeTool = scene.treeTool

        layout.prop(treeTool, "barkDeformities")
        layout.prop(treeTool, "startingSplitChance")
        layout.prop(treeTool, "splitChanceGain")

        layout.separator()

        layout.operator("wm.create_tree")


class CreateTree(Operator):
    bl_idname = "wm.create_tree"
    bl_label = "Create Tree"

    def execute(self, context):
        scene = context.scene
        treeTool = scene.treeTool

        print("I work!")
        print("bool state:", treeTool.barkDeformities)
        print("int value:", treeTool.startingSplitChance)
        print("float value:", treeTool.splitChanceGain)

        return {'FINISHED'}

#======== Class Registration ====================
classes = (
    TreeBranchingProprieties,
    TreeCreationPannel,
    CreateTree
)
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    # ============== Important!(register properties)==
    bpy.types.Scene.treeTool = PointerProperty(type=TreeBranchingProprieties)
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.treeTool

if __name__ == "__main__":
    register()

