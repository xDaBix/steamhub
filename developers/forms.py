from django import forms
from django.core.exceptions import ValidationError
from .models import Developer, Game, GameImage
from datetime import date, timedelta
from django.core.validators import MinLengthValidator
from django.forms import modelformset_factory


class Registration(forms.Form):
    firstname = forms.CharField(max_length=50, label='First Name')
    lastname = forms.CharField(max_length=50, label='Last Name')
    contactno = forms.CharField(
        max_length=10, 
        label='Contact Number',
        validators=[MinLengthValidator(10)]
    )
    email = forms.EmailField(max_length=100, label='Email')
    username = forms.CharField(max_length=30, label='Username')  
    password = forms.CharField(
        max_length=50, 
        label='Password',
        widget=forms.PasswordInput
    )
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')],
        label='Gender',
        widget=forms.Select(attrs={'class': 'gender-dropdown'})
    )
    
    
    max_date = (date.today() - timedelta(days=365*16)).strftime('%Y-%m-%d')
    
    date_of_birth = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'min': '1900-01-01',
            'max': max_date
        })
    )


class GameUploadForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'game_type', 'description', 'price', 'release_date', 'version', 'game_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['version'].initial = 1
        self.fields['version'].disabled = True 
    def clean_game_file(self):
        game_file = self.cleaned_data.get('game_file')
        if game_file:
            if not game_file.name.endswith('.zip'):
                raise ValidationError("Only .zip files are allowed for game upload.")
            
            max_size_mb = 5000
            if game_file.size > max_size_mb * 1024 * 1024:
                raise ValidationError(f"File size should not exceed {max_size_mb} MB.")
        return game_file


class GameImageForm(forms.ModelForm):
    class Meta:
        model = GameImage
        fields = ['image']

    
    image = forms.ImageField(required=False)



GameImageFormSet = modelformset_factory(GameImage, form=GameImageForm, extra=3)
