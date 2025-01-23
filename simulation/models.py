from django.db import models

class CustomerArrival(models.Model):
    number_of_customers = models.IntegerField()
    max_serves_time = models.IntegerField()
    max_arrived_time = models.IntegerField()
    max_serves2_time = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Customers: {self.number_of_customers}, Max_serves: {self.max_serves_time}, Max: {self.max_arrived_time}"

