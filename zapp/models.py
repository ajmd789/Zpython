from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    """用户扩展信息模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='关联用户')
    phone = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号')
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name='昵称')
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name='头像URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'
    
    def __str__(self):
        return f'{self.user.username} 的扩展信息'


class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户')
    name = models.CharField(max_length=255, verbose_name='药品名称')
    description = models.TextField(blank=True, verbose_name='药品描述')
    dosage = models.CharField(max_length=100, verbose_name='服用剂量')
    total_quantity = models.IntegerField(default=0, verbose_name='初始总量')
    current_quantity = models.IntegerField(default=0, verbose_name='当前剩余量')
    unit = models.CharField(max_length=20, default='片', verbose_name='单位')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '药品信息'
        verbose_name_plural = '药品信息'

    def __str__(self):
        return f'{self.name} ({self.current_quantity}/{self.total_quantity} {self.unit})'


class MedicationSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ('morning', '早晨'),
        ('noon', '中午'),
        ('evening', '晚上'),
        ('custom', '自定义'),
    ]

    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='schedules', verbose_name='药品')
    time = models.TimeField(verbose_name='服用时间')
    frequency_type = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name='频次类型')
    days_of_week = models.CharField(max_length=20, default='1,2,3,4,5,6,7', verbose_name='适用星期')
    dosage_amount = models.IntegerField(default=1, verbose_name='每次服用数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '用药计划'
        verbose_name_plural = '用药计划'

    def __str__(self):
        return f'{self.medication.name} - {self.get_frequency_type_display()} at {self.time}'


class MedicationRecord(models.Model):
    STATUS_CHOICES = [
        ('taken', '已服用'),
        ('missed', '未服用'),
        ('skipped', '跳过'),
    ]

    schedule = models.ForeignKey(MedicationSchedule, on_delete=models.CASCADE, related_name='records', verbose_name='关联计划')
    date = models.DateField(verbose_name='记录日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='missed', verbose_name='状态')
    taken_at = models.DateTimeField(null=True, blank=True, verbose_name='实际服用时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用药记录'
        verbose_name_plural = '用药记录'
        unique_together = ['schedule', 'date']

    def __str__(self):
        return f'{self.schedule.medication.name} - {self.date} - {self.get_status_display()}'

