from django import forms

class NumberOfCustomersForm(forms.Form):
    number_of_customers = forms.IntegerField(min_value=1, label="Number of customers", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    max_arrived_time = forms.IntegerField(min_value=1, label="Max arrived time", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    max_serves_time = forms.IntegerField(min_value=1, label="server one max time ", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    max_serves2_time = forms.IntegerField(min_value=1, label="server two max time ", widget=forms.NumberInput(attrs={'class': 'form-control'}))



    def __init__(self, *args, **kwargs):
        server_id = kwargs.pop('server_id', None)  # احصل على server_id من المعاملات
        super().__init__(*args, **kwargs)

        # اجعل حقل max_serves2_time اختياريًا إذا لم يكن server_id يساوي 2
        if server_id != 2:
            self.fields['max_serves2_time'].required = False