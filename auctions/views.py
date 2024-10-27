from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Listing, Image, Bid, Wishlist
from .forms import ListingForm, ImageForm, CommentForm
from django.forms import modelformset_factory
from django.utils import timezone
from django.contrib import messages


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    return render(request, 'auctions/index.html', {'listings': active_listings})


@login_required
def create_listing(request):
    ImageFormSet = modelformset_factory(
        Image, form=ImageForm, extra=3)  # Allows multiple images

    if request.method == 'POST':
        listing_form = ListingForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES,
                               queryset=Image.objects.none())

        if listing_form.is_valid() and formset.is_valid():
            listing = listing_form.save(commit=False)  # Don't save yet
            listing.user = request.user  # Set the current user
            listing.save()  # Now save the listing

            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    Image.objects.create(listing=listing, image=image)

            return redirect('view_listing', listing_name=listing.name)
    else:
        listing_form = ListingForm()
        formset = ImageFormSet(queryset=Image.objects.none())

    return render(request, 'auctions/post_ad.html', {'listing_form': listing_form, 'formset': formset})


def view_listing(request, listing_name):
    listing = get_object_or_404(Listing, name=listing_name)
    images = listing.images.all()  # Retrieve all images associated with the listing
    today = timezone.now().date()

    # Get the highest bid for the listing, if any
    highest_bid = Bid.objects.filter(
        listing=listing).order_by('-amount').first()
    highest_bidder = highest_bid.user if highest_bid else None

    # Automatically update is_active status if closing date has passed
    if listing.closing_date < today and listing.is_active:
        listing.is_active = False
        listing.save()

    # Add this line to explicitly check if current user is winner
    is_winner = (highest_bidder ==
                 request.user and not listing.is_active and listing.closing_date < today)

    # Handling comments
    comments = listing.comments.all()  # Get comments related to this listing
    form = CommentForm()

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                # Prevent users from commenting on their own listings
                if request.user != listing.user:
                    comment = form.save(commit=False)
                    comment.listing = listing
                    comment.user = request.user
                    comment.save()
                    messages.success(request, 'Your comment has been added!')
                else:
                    messages.warning(
                        request, 'You cannot comment on your own listing.')
                return redirect('view_listing', listing_name=listing_name)

    context = {
        'listing': listing,
        'images': images,
        'highest_bidder': highest_bidder,
        'today': today,
        'highest_bid': highest_bid,
        'comments': comments,
        'form': form,
        'is_winner': is_winner,
    }
    return render(request, 'auctions/listing.html', context)


def filtered_listings(request, category_name):
    # Normalize the category name to match the format in the database
    category_name = category_name.capitalize()  # Capitalize the first letter

    # Filter listings based on the category name
    listings = Listing.objects.filter(category=category_name)

    return render(request, 'auctions/index.html', {'listings': listings, 'category': category_name})


@login_required
def delete_listing(request, listing_name):
    listing = get_object_or_404(Listing, name=listing_name)

    # Check if the current user is the creator of the listing
    if request.user == listing.user:  # Assuming you have a 'user' field in Listing model
        listing.delete()  # Delete the listing
        return redirect('index')  # Redirect to the index page after deletion
    else:
        return render(request, 'auctions/error.html', {'message': 'You do not have permission to delete this listing.'})


@login_required
def place_bid(request, listing_name):
    listing = get_object_or_404(Listing, name=listing_name)

    # Check if the listing is still active and not closed
    if not listing.is_active or listing.closing_date < timezone.now().date():
        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'message': "Bidding has closed."
        })

    if request.method == 'POST':
        bid_amount = int(request.POST.get('bid_amount', 0))

        # Validate the bid amount
        if bid_amount < listing.reservation_price:
            messages.error(
                request, "Your bid must be at least the reservation price.")
        elif bid_amount >= listing.highest_bid + 50:
            # Create a new bid
            Bid.objects.create(
                listing=listing, user=request.user, amount=bid_amount)
            listing.highest_bid = bid_amount
            listing.save()
            messages.success(request, "Your bid has been placed successfully!")
            return redirect('view_listing', listing_name=listing_name)
        else:
            # Add an error message if the bid is too low
            messages.error(request, f'''Your bid must be at least R{
                           listing.highest_bid + 50}.''')

    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'images': listing.images.all()
    })


def add_to_wishlist(request, listing_name):
    listing = get_object_or_404(Listing, name=listing_name)
    if request.user.is_authenticated and request.user != listing.user:
        Wishlist.objects.get_or_create(user=request.user, listing=listing)
        messages.success(request, f'Added "{listing.name}" to your wishlist!')
    return redirect('view_listing', listing_name=listing_name)


def remove_from_wishlist(request, listing_name):
    listing = get_object_or_404(Listing, name=listing_name)
    if request.user.is_authenticated:
        Wishlist.objects.filter(user=request.user, listing=listing).delete()
    return redirect('view_listing', listing_name=listing_name)


def view_wishlist(request):
    # Get the user's wishlist
    wishlist_items = Wishlist.objects.filter(
        user=request.user).select_related('listing')

    return render(request, 'auctions/wishlist.html', {
        'wishlist_items': wishlist_items,
    })


def search_listings(request):
    query = request.GET.get('q')
    category = request.GET.get('category')

    # Start with all listings
    listings = Listing.objects.all()

    # Filter by category if specified
    if category:
        listings = listings.filter(category=category)

    # Filter by query if specified
    if query:
        # or use description__icontains for more flexibility
        listings = listings.filter(name__icontains=query)

    return render(request, 'auctions/index.html', {'listings': listings})


@login_required
def close_auction(request, listing_name):
    listing = get_object_or_404(Listing, name=listing_name)

    # Check if the logged-in user is the owner of the listing
    if request.user == listing.user:
        # Close the auction and set the highest bidder as the winner
        listing.close_auction()
        messages.success(request, f'''The auction for {
                         listing.name} has been closed.''')
    else:
        messages.error(
            request, "You are not authorized to close this auction.")

    return redirect('view_listing', listing_name=listing.name)
