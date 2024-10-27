from django import forms
from django.utils import timezone
from .models import Listing, Image, Comment


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['name', 'description',
                  'reservation_price', 'closing_date', 'category']
        widgets = {
            'closing_date': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'type': 'date',
            }),
        }

    def save(self, commit=True):
        listing = super().save(commit=False)
        listing.is_active = True  # Ensure new listings are active
        if commit:
            listing.save()
        return listing

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_closing_date(self):
        closing_date = self.cleaned_data.get('closing_date')
        if closing_date:
            if closing_date < timezone.now().date():
                raise forms.ValidationError(
                    "The closing date cannot be in the past.")
        return closing_date


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add a comment...',
                'class': 'form-control',
                'style': 'resize: none;',  # Prevent resizing if you want
                'maxlength': 500,  # Optional: limit the number of characters
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the label for the 'content' field
        self.fields['content'].label = ''
