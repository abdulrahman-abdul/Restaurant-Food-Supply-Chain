
from django.db import models


class restaurant_details(models.Model):
    client_id=models.CharField(max_length=200,null=True)
    name=models.CharField(max_length=100)
    shop_name = models.CharField(max_length=100)
    email=models.EmailField(unique=True,max_length=200,null=True)
    password=models.CharField(max_length=200,null=True)
    phone_number=models.PositiveBigIntegerField()
    city = models.CharField(null=True,max_length=100)

    state = models.CharField(max_length=200, null=True)

    r_approve=models.BooleanField(null=True,default=0)
    r_reject = models.BooleanField(null=True, default=0)
    r_login= models.BooleanField(null=True, default=0)
    r_logout = models.BooleanField(null=True, default=0)
    full_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_done = models.BooleanField(null=True, default=0)
    dl_approve=models.BooleanField(default=False, null=True)
    dl_reject=models.BooleanField(default=False, null=True)
    s_report = models.FileField(upload_to='pdf_reports/', null=True, blank=True)
    pdf_done = models.BooleanField(default=False, null=True)
    f_approve = models.BooleanField(default=False, null=True)
    f_reject = models.BooleanField(default=False, null=True)
    total_done = models.BooleanField(null=True, default=0)


class restaurant_order(models.Model):
    food_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    Br_id = models.CharField(max_length=200, null=True)


class modules_registration(models.Model):
    client_id = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=100)
    category= models.CharField(max_length=200, null=True)

    email = models.EmailField(unique=True,max_length=200, null=True)
    password = models.CharField(max_length=200, null=True)
    phone_number = models.PositiveBigIntegerField()
    approve = models.BooleanField(null=True, default=0)
    reject = models.BooleanField(null=True, default=0)
    dl_login=models.BooleanField(null=True, default=0)
    su_login = models.BooleanField(null=True, default=0)
    su_client_id=models.CharField(max_length=200,null=True)
    dl_client_id = models.CharField(max_length=200, null=True)


class temp_table (models.Model):
    food_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='food_images/',blank=True, null=True)
    Br_id = models.CharField(max_length=200, null=True)
    f_login= models.BooleanField(null=True, default=0)
    quantity = models.PositiveBigIntegerField(default=1)
    Total_price=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    client_id = models.CharField(max_length=200, null=True)
    f_encrypt = models.BooleanField(default=False)
    f_decrypt = models.BooleanField(default=False)
    f_key = models.CharField(max_length=200, null=True)
    f_getkey = models.BooleanField(default=False)
    f_keyenter = models.CharField(max_length=200, null=True)
    f_keycheck = models.BooleanField(default=False)

    dec_food_name = models.CharField(max_length=100,null=True)
    dec_price =  models.CharField(max_length=100,null=True)
    dec_quantity = models.CharField(max_length=100,null=True)
    dec_Total_price =  models.CharField(max_length=100,null=True)
    su_done = models.BooleanField(default=False)
    Carbon_Footprint=models.FloatField(null=True)
    Water_Usage=models.FloatField(null=True)
    Energy_Consumption=models.FloatField(null=True)
    fview = models.BooleanField(default=False, null=True)
    f_report = models.FileField(upload_to='pdf_reports/', null=True, blank=True)
    status = models.CharField(max_length=100, default="pending")
    payment_done = models.BooleanField(null=True, default=0)
    total_done = models.BooleanField(null=True, default=0)







