from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Skill

class UserRegisterForm(UserCreationForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,  # Öğretmenler için isteğe bağlı hale getiriyoruz
        label="Skills (Only for Teachers)"
    )

    class Meta:
        model = User
        fields = ['username', 'role', 'skills', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # "manager" seçeneğini çıkararak choices'ı yeniden tanımlıyoruz
        self.fields['role'].choices = [
            (choice[0], choice[1]) for choice in User.ROLE_CHOICES if choice[0] != 'manager'
        ]
        # Role alanını kontrol ederek skills alanının görünürlüğünü ayarlıyoruz
        if 'role' in self.data:
            self.fields['skills'].widget.attrs['style'] = 'display:none;' if self.data['role'] != 'teacher' else ''
        elif 'instance' in kwargs and kwargs['instance'].role != 'teacher':
            self.fields['skills'].widget.attrs['style'] = 'display:none;'

    def clean_skills(self):
        role = self.cleaned_data.get('role')
        skills = self.cleaned_data.get('skills')
        if role != 'teacher' and skills:
            raise forms.ValidationError("Only teachers can have skills.")
        return skills


class UserUpdateForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,  # Öğretmenler için isteğe bağlı hale getiriyoruz
        label="Skills (Only for Teachers)"
    )

    class Meta:
        model = User
        fields = ['username', 'role', 'skills']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # "manager" seçeneğini çıkararak choices'ı yeniden tanımlıyoruz
        self.fields['role'].choices = [
            (choice[0], choice[1]) for choice in User.ROLE_CHOICES if choice[0] != 'manager'
        ]
        # Role alanını kontrol ederek skills alanının görünürlüğünü ayarlıyoruz
        if 'role' in self.data:
            self.fields['skills'].widget.attrs['style'] = 'display:none;' if self.data['role'] != 'teacher' else ''
        elif 'instance' in kwargs and kwargs['instance'].role != 'teacher':
            self.fields['skills'].widget.attrs['style'] = 'display:none;'

    def clean_skills(self):
        role = self.cleaned_data.get('role')
        skills = self.cleaned_data.get('skills')
        if role != 'teacher' and skills:
            raise forms.ValidationError("Only teachers can have skills.")
        return skills

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter skill name'}),
        }