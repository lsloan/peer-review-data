# -*- coding: utf-8 -*-
import logging
from typing import Self  # Cannot find reference 'Self' in 'typing.pyi'

from django.db import models

from canvasData import *

LOGGER = logging.getLogger(__name__)


class Course(models.Model):
    class Meta:
        db_table = Course.__name__.lower()

    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    course_code = models.TextField()

    @classmethod
    def fromCanvasCourse(cls, c: CanvasCourse) -> Self:
        return cls(c.id, c.name, c.course_code)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.course_code}"'


class User(models.Model):
    class Meta:
        db_table = User.__name__.lower()

    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    sortable_name = models.TextField()
    login_id = models.TextField()

    @classmethod
    def fromCanvasUser(cls, u: CanvasUser) -> Self:
        return cls(u.id, u.name, u.sortable_name, u.login_id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.login_id}"'


class Assignment(models.Model):
    class Meta:
        db_table = Assignment.__name__.lower()

    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasAssignment(cls, a: CanvasAssignment) -> Self:
        return cls(a.id, a.name, a.course_id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.name}"'


class Rubric(models.Model):
    class Meta:
        db_table = Rubric.__name__.lower()

    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasRubricAndAssignment(cls, r: CanvasRubric,
                                      a: CanvasAssignment) -> Self:
        return cls(r.id, r.title, a.id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.title}" ' \
               f'({self.assignment})'


class Criterion(models.Model):
    class Meta:
        db_table = 'criterion'
        # db_table = Criterion.__name__.lower()  # XXX: error?!

    id = models.IntegerField(primary_key=True)
    description = models.TextField()
    long_description = models.TextField()
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE,
                               related_name='criteria')

    @classmethod
    def fromCanvasCriterionAndRubric(
            cls, c: CanvasCriteria, r: Rubric) -> Self:
        return cls(c.id, c.description, c.longDescription, r.id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'"{self.description}" ({self.rubric})'


class Submission(models.Model):
    class Meta:
        db_table = Submission.__name__.lower()

    id = models.IntegerField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasSubmission(cls, s: CanvasSubmission) -> Self:
        return cls(s.id, s.assignment_id, s.user_id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'({self.assignment}; {self.user})'


class Assessment(models.Model):
    class Meta:
        db_table = 'assessment'
        # db_table = Assessment.__name__.lower()  # XXX: error?!

    id = models.IntegerField(primary_key=True)
    assessor = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasAssessment(cls, a: CanvasAssessment) -> Self:

        submission: Submission = Submission.objects.get(id=a.submissionId)
        if submission:
            LOGGER.debug(f'Got ({submission})!')
        else:
            LOGGER.info('Could not find submission with ID '
                        f'({a.submissionId})!')
        return cls(a.id, a.assessorId, a.submissionId)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'({self.assessor}; {self.submission})'


class Comment(models.Model):
    """
    Strictly speaking, this should be `AssessmentComment`.  This app will
    probably never process any other kind of comment, though, so we'll use
    a short name here for brevity.
    """

    class Meta:
        db_table = 'comment'
        # db_table = Comment.__name__.lower()  # XXX: error?!

    # Canvas does not give unique IDs for each comment!
    id = models.AutoField(primary_key=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)
    comments = models.TextField()

    @classmethod
    def fromCanvasCommentAndAssessment(
            cls, c: CanvasComment, a: Assessment) -> Self:
        return cls(None, a.id, c.criterionId, c.comments)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'({self.assessment}; {self.criterion}; {self.comments})'
