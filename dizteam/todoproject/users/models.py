from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os

# Create your models here.

def user_profile_image_path(instance, filename):
    # Генерируем путь для загрузки изображения: MEDIA_ROOT/profile_images/user_<id>/<filename>
    return f'profile_images/user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(default='profile_images/default.png', upload_to=user_profile_image_path)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def save(self, *args, **kwargs):
        # Сначала сохраняем модель
        super().save(*args, **kwargs)
        
        # Затем обрабатываем изображение, если оно существует
        if self.profile_image:
            img_path = self.profile_image.path
            if os.path.exists(img_path):
                img = Image.open(img_path)
                
                # Если изображение больше 300x300, то изменим его размер
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(img_path)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
