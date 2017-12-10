import datetime
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

class MyChoice(models.Model):
    mychoice_text = models.CharField(max_length=200)
    myvotes = models.IntegerField(default=0)
    history = HistoricalRecords()

    def __str__(self):
        return self.mychoice_text

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    mychoice = models.ForeignKey(MyChoice, on_delete=models.CASCADE)
    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    YEAR_IN_SCHOOL_CHOICES = (
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
    )
    year_in_school = models.CharField(
        max_length=2,
    )
    history = HistoricalRecords()
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.question_text

class newChoice(models.Model):
    newquestion = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)
    history = HistoricalRecords()

    def __str__(self):
        return self.newquestion


class Choice(models.Model):
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    newchoice = models.ForeignKey(newChoice, on_delete=models.CASCADE)


    def __str__(self):
        return self.choice_text
# Create your models here.

