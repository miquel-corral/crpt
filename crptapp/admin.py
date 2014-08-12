from django.contrib import admin
import crptapp.models

admin.site.register(crptapp.models.Hazard)
admin.site.register(crptapp.models.HazardCategory)
admin.site.register(crptapp.models.Responder)
admin.site.register(crptapp.models.City)
admin.site.register(crptapp.models.SpatialUnitType)
admin.site.register(crptapp.models.Assessment)
admin.site.register(crptapp.models.Role)
admin.site.register(crptapp.models.Actor)
admin.site.register(crptapp.models.ActorRole)
admin.site.register(crptapp.models.RiskAssessmentSection)
admin.site.register(crptapp.models.RiskAssessmentQuestion)
admin.site.register(crptapp.models.RiskAssessmentQuestionStatement)
admin.site.register(crptapp.models.AssessmentRAQuestionStatement)
admin.site.register(crptapp.models.AssessmentHazardCausality)
admin.site.register(crptapp.models.RiskAssessmentCausalityQuestion)
admin.site.register(crptapp.models.RiskAssessmentCausalityQuestionStatement)
admin.site.register(crptapp.models.AssessmentRACausalityQuestionStatement)
admin.site.register(crptapp.models.CapacityAssessmentSection)
admin.site.register(crptapp.models.CapacityAssessmentSubsection)
admin.site.register(crptapp.models.CapacityAssessmentQuestionSet)
admin.site.register(crptapp.models.CapacityAssessmentQuestion)
admin.site.register(crptapp.models.CapacityAssessmentStatement)
admin.site.register(crptapp.models.AssessmentCAYESNOStatement)
admin.site.register(crptapp.models.AssessmentCAEffectivenessStatement)
admin.site.register(crptapp.models.AssessmentCAMeetingFrequencyStatement)
admin.site.register(crptapp.models.AssessmentCAMeetingAttendanceStatement)
admin.site.register(crptapp.models.AssessmentCAGenericStatement)
