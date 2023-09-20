from django.contrib import admin

from repairs.models import (
    Instruction,
    InstructionChecklist,
    InstructionChecklistQuestion,
    InstructionContactNote,
    InstructionNote,
    InstructionSpecification,
    Measurement,
    MeasurementImage,
    Project,
    ProjectContact,
)

admin.site.register(Measurement)
admin.site.register(MeasurementImage)
admin.site.register(Project)
admin.site.register(ProjectContact)
admin.site.register(Instruction)
admin.site.register(InstructionNote)
admin.site.register(InstructionContactNote)
admin.site.register(InstructionSpecification)
admin.site.register(InstructionChecklist)
admin.site.register(InstructionChecklistQuestion)
