from django.db import models

class Story(models.Model):
    storyName = models.CharField(max_length=31)
    
    def save(self, *args, **kwargs):
        if self.id is None:
            super(Story, self).save(*args, **kwargs)

