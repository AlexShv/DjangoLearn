from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    photo = models.ImageField(upload_to='users_photos/', blank=True)
    is_teacher = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=65, help_text='Enter a category')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Course(BaseModel):
    title = models.CharField(max_length=85, help_text='Enter a title to the course')
    image = models.ImageField(upload_to='courses_photos')
    description = models.TextField(help_text='Information about the course')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)  # Fixed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Lesson(BaseModel):
    title = models.CharField(max_length=85, help_text='Enter a title to the lesson')
    content = models.TextField(help_text='Information about lesson')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Assignment(BaseModel):
    title = models.CharField(max_length=95, help_text='Title of the assignment')
    description = models.TextField(help_text='Assignment information')
    due_date = models.DateField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Assignment {self.title} for lesson {self.lesson}'


class Subscription(BaseModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(BaseModel):
    description = models.TextField(help_text='Enter a comment')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description


class StudentProgress(BaseModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    progress = models.DecimalField(max_digits=5, decimal_places=2)
    completed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Student\'s progress"


class Chat(BaseModel):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='chat')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(BaseModel):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')  # Changed related_name
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)


class Reaction(BaseModel):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reactions')  # Changed related_name

    REACTION_CHOICES = (
        ('like', '👍'),
        ('sparkles', '🌟'),
        ('grinning face', '😄'),
        ('dislike', '👎'),
        ('disappointed', '😞'),
        ('confused', '😕'),
    )

    type_of_reaction = models.CharField(max_length=20, choices=REACTION_CHOICES, help_text='Reaction for the message')

    def get_reaction(self):
        for choice in self.REACTION_CHOICES:
            if choice[0] == self.type_of_reaction:
                return choice[1]
        return 'Unknown reaction'

    def __str__(self):
        return f'{self.user} reacted {self.message} with {self.get_reaction()}'
