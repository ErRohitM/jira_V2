import datetime

from django.db import models
from autoslug import AutoSlugField

from users.models import BaseUser
from common.models import BaseModels

class Organization(BaseModels):
    """
    Represents an organization entity.
    Inherits timestamp and common fields from BaseModels.
    """
    name = models.CharField(max_length=100)
    # contact_email = models.EmailField() # manager / owner cont email
    users = models.ManyToManyField(BaseUser, related_name='belonging_organization')

    slug = AutoSlugField(populate_from='get_org_slug', unique=True, blank=True)

    class Meta:
        ordering = ['name']  # object ordering

    # generates slug
    def get_org_slug(self):
        return f"{self.name.lower().replace(' ', '-')}_{self.created_at}"

    def __str__(self):
        return self.slug or self.name

class Projects(BaseModels):
    """
    Represents an Project entity
    Project - organization dependent
    inherits BaseModel fields
    """

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
    ]

    # many-to-one relation with organization
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    slug = AutoSlugField(populate_from="get_project_slug", unique=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['organization', 'name']]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

    # generate custom project slug
    def get_project_slug(self):
        return f"{self.name}_{self.organization.name}"

    @property
    def task_count(self):
        return self.tasks.count()

    @property
    def completed_tasks_count(self):
        return self.tasks.filter(status='DONE').count()

    @property
    def completion_rate(self):
        if self.task_count == 0:
            return 0
        return (self.completed_tasks_count / self.task_count) * 100


class Tasks(BaseModels):
    """
    Task model - project dependent
    inherits BaseModel fields
    """

    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
    ]

    TASK_GROUP_CHOICES = [
        ('NEW_TASK', 'New Task'),
        ('FIX_ISSUE', 'Fix Issue')
    ]

    # many-to-one relation with project
    project = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=200)
    type = models.CharField(max_length=55, choices=TASK_GROUP_CHOICES, default='NEW_TASK') # task type
    description = models.TextField(blank=True)

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='HIGH')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')

    """
    Assigned to User
    single task can be assigned to multiple members
    single member can work on multiple tasks    
    """
    assignees = models.ManyToManyField(BaseUser, related_name='assigned_tasks')
    due_date = models.DateField(null=False, default=datetime.date.today() + datetime.timedelta(days=30)) # 30 days validity by default

    # optional attachments
    attachments = models.FileField(upload_to='optional_uploads/', blank=True, null=True)
    slug = AutoSlugField(populate_from="get_task_slug")

    class Meta:
        ordering = ['-created_at']

    # generate custom task slug
    def get_task_slug(self):
        return f"{self.type}_{self.title}_{self.project.name}"

    def __str__(self):
        return f"{self.project.name} - {self.title}"
