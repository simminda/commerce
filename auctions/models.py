from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Listing(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    description = models.TextField()
    reservation_price = models.IntegerField()  # Minimum bid amount
    listing_date = models.DateField(auto_now_add=True)
    closing_date = models.DateField()
    # Track highest bid, set to 0 initially
    highest_bid = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)  # Active or inactive listing
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    winner = models.ForeignKey(
        User, related_name="won_listings", null=True, blank=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=50, choices=[
        ('Digital', 'Digital'),
        ('Home and Garden', 'Home and Garden'),
        ('Toys', 'Toys'),
        ('Fashion', 'Fashion'),
        ('Lifestyle', 'Lifestyle'),
        ('Automotive', 'Automotive'),
        ('Other', 'Other'),
    ])

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new listing
            # Set highest bid to reservation price initially
            self.highest_bid = self.reservation_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def close_auction(self):
        """Method to close the auction, set the highest bidder as winner, and make listing inactive."""
        if self.is_active:
            highest_bid = self.bid_set.order_by('-amount').first()
            if highest_bid:
                self.winner = highest_bid.user
            self.is_active = False
            self.save()


class Image(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')

    def __str__(self):
        return f"Image for {self.listing.name}"


class Bid(models.Model):
    amount = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        # Validate bid amount
        if self.amount <= self.listing.highest_bid:
            raise ValidationError(
                "Bid must be higher than current highest bid")
        if self.amount < self.listing.reservation_price:
            raise ValidationError("Bid must be at least the reservation price")

    def save(self, *args, **kwargs):
        # Clean the instance before saving
        self.full_clean()

        # Save the bid
        super().save(*args, **kwargs)

        # Update the listing's highest bid
        if self.amount > self.listing.highest_bid:
            self.listing.highest_bid = self.amount
            self.listing.save()

    def __str__(self):
        return f"{self.user.username} bid {self.amount} on {self.listing.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wishlist')
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='wishlisted_by')

    class Meta:
        unique_together = ('user', 'listing')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.user.username}'s wishlist"


class Comment(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
