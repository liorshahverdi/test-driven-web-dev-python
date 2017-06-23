from django.db import models
import uuid

class List(models.Model):
	uuid = models.UUIDField(unique=True, default='')

class Item(models.Model):
	text = models.TextField(default='')
	list = models.ForeignKey(List, default=None)