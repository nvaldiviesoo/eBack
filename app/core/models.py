"""
Database models for the core app.
"""
import uuid
import os

from django.db import models
from django.contrib.auth.models import (
  AbstractBaseUser,
  BaseUserManager,
  PermissionsMixin
)

def product_image_file_path(instance, filename):
  """Generate file path for new product image"""
  ext = os.path.splitext(filename)[1]
  filename = f'{uuid.uuid4()}.{ext}'
  return os.path.join('uploads', 'products', filename )

class UserManager(BaseUserManager):
  """Manager for user."""

  def create_user(self, email, password=None, **extra_fields):
    """Creates, save and return a new user"""
    if not email:
      raise ValueError('Users must have an email address')
    user = self.model(email=self.normalize_email(email), **extra_fields)
    user.set_password(password)
    user.save(using=self._db)

    return user

  def create_superuser(self, email, password):
    """Creates and saves a new superuser"""
    user = self.create_user(email, password)
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)

    return user


class User(AbstractBaseUser, PermissionsMixin):
  """User in the system"""
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  email = models.EmailField(max_length=320, unique=True)
  name = models.CharField(max_length=50)
  balance = models.PositiveIntegerField(default=100000)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)

  objects = UserManager()

  USERNAME_FIELD = 'email'


class Product(models.Model):
  """Products in the system"""

  CATEGORY_OPTIONS = (
    ('Crop Tops', 'Crop Tops'),
    ('Hoodies', 'Hoodies'),
    ('Joggers', 'Joggers'),
    ('Shorts', 'Shorts'),
    ('Sports Bra', 'Sports Bra'),
    ('Underwear', 'Underwear'),
  )
  GENDER_OPTIONS = (
    ('Female', 'Female'),
    ('Male', 'Male'),
    ('Unisex', 'Unisex')
  )
  SIZE_OPTIONS = (
    ('XS', 'XS'),
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('XXL', 'XXL'),
  )

  COLOR_OPTIONS = (
    ('Red', 'Red'),
    ('Yellow', 'Yellow'),
    ('Blue', 'Blue'),
    ('Black', 'Black'),
    ('White', 'White'),
    ('Green', 'Green'),
    ('Orange', 'Orange'),
    ('Purple', 'Purple'),
    ('Pink', 'Pink'),
    ('Brown', 'Brown'),
    ('Grey', 'Grey'),
    ('Beige', 'Beige'),
    ('Other', 'Other')
  )

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=75)
  description = models.TextField()
  price = models.PositiveIntegerField(default=0)
  discount_percentage = models.PositiveIntegerField(default=0, null=True, blank=True)
  image = models.ImageField(null=True, upload_to='products-images/', blank=True)
  category = models.TextField(choices=CATEGORY_OPTIONS, null=True)
  gender = models.TextField(choices=GENDER_OPTIONS, null=True)
  size = models.TextField(choices=SIZE_OPTIONS, null=False, blank=False)
  color = models.TextField(choices=COLOR_OPTIONS, null=False, blank=False, default='Other')
  quantity = models.PositiveIntegerField(default=0, null=False, blank=False)

  user = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='products'
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name

class OrderStatus(models.TextChoices):
  PROCESSING = 'Processing'
  SHIPPED = 'Shipped'
  DELIVERED = 'Delivered'
  CANCELLED = 'Cancelled'

class PaymentStatus(models.TextChoices):
  PAID = 'PAID'
  UNPAID = 'UNPAID'

class PaymentMode(models.TextChoices):
  COD = 'COD'
  CARD = 'Card'

class Order(models.Model):
  """Orders in the system"""

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

  street_address = models.CharField(max_length=50, default='', blank=False)
  city = models.CharField(max_length=50, default='', blank=False)
  zip_code = models.CharField(max_length=10, default='' ,blank=False)
  country = models.CharField(max_length=20, default='', blank=False)
  total_amount = models.PositiveIntegerField(default=0)
  payment_status = models.CharField(
    max_length=10,
    choices=PaymentStatus.choices,
    default=PaymentStatus.UNPAID
  )
  status = models.CharField(max_length=15,
    choices=OrderStatus.choices,
    default=OrderStatus.PROCESSING)

  payment_mode = models.CharField(
    max_length=10,
    choices=PaymentMode.choices,
    default=PaymentMode.COD
  )

  user = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    related_name='orders',
    null=True
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  def __str__(self):
    return str(self.id)


class OrderItem(models.Model):
  """Order items in the system"""

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  quantity = models.PositiveIntegerField(default=0)
  price = models.PositiveIntegerField(default=0)
  product = models.ForeignKey(
    Product,
    on_delete=models.SET_NULL,
    null=True
  )

  order = models.ForeignKey(
    Order,
    on_delete=models.CASCADE,
    null=True,
    related_name='order_items'
  )

  def __str__(self):
    return str(self.id)