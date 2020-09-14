from datetime import datetime

from django.db import models
from authApp.models import Facility, Users


class Questionnaire (models.Model):
    name = models.CharField(max_length=15)
    description = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    active_till = models.DateField(default=datetime.now)

    class Meta:
        db_table = "Questionnaires"


class Question (models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    question =  models.CharField(max_length=50)
    question_type = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE)


    class Meta:
        db_table = "Questions"

class Answer (models.Model):
    question= models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE, default=1)

    class Meta:
        db_table = "Answers"


class Response (models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    open_text = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = "Responses"


class Patient_Consent(models.Model):
    ccc_number = models.CharField(max_length=15)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)

    class Meta:
        db_table = "PatientConsent"


class Started_Questionnaire (models.Model):
    ccc_number = models.CharField(max_length=15)
    firstname = models.CharField(max_length=30)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)

    class Meta:
        db_table = "Started_Questionnaire"


class Facility_Questionnaire (models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)

    class Meta:
        db_table = "Facility_Questionnaire"
