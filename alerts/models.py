from django.db import models

ALERT_MEDIA = (
    (1, 'TV'),
    (2, 'Newspaper'),
    (3, 'Magazine'),
    (4, 'Web'),
    )


#occurences of books in media
class Alert(models.Model):
    #book's author
    author = models.CharField(max_length=255)
    #book's title
    title = models.CharField(max_length=255)

    #date occurred
    date = models.DateTimeField()
    #media where it occurred (can make another class to store more detailed)
    media = models.IntegerField(default=1, choices=ALERT_MEDIA)
    
    #importance level of the alert (MOTOR's measure?)
    level = models.IntegerField(default=1)



