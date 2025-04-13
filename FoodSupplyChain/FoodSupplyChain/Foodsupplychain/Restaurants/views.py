from django.shortcuts import render,redirect
from django.contrib import messages
from admins.models import restaurant_details,restaurant_order,modules_registration,temp_table
from django.core.mail import send_mail
from django.db.models import Sum

def re_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        shop_name = request.POST.get("shopname")
        city = request.POST.get("city")
        state = request.POST.get("state")

        # Check if the email address is a valid Gmail address
        if not email.endswith('@gmail.com'):
            messages.error(request, "Only Gmail addresses are allowed.")
            return render(request, 'restaurant/re_register.html')

        # Check if the email is unique
        if restaurant_details.objects.filter(email=email).exists():
            messages.error(request, "This email address is already registered.")
            return render(request, 'restaurant/re_register.html')

        # Save the new registration
        obj = restaurant_details(name=name, email=email, phone_number=phone, shop_name=shop_name,city=city,state=state)
        obj.save()
        messages.info(request, f"{obj.shop_name}: Restaurant  Registration  Successful")
        return render(request, 'restaurant/re_register.html')



    return render(request,'restaurant/re_register.html')

def re_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Check if a user with the given email exists
            user = restaurant_details.objects.get(email=email)

            # Check if the provided password matches
            if user.password == password:
                user.r_login = True
                user.save()
                messages.success(request, f"{user.shop_name}: Restaurant Login Successful")
                return redirect('/re_home/')
            else:
                messages.error(request, "Invalid email or password")
                return render(request, 'restaurant/re_register.html')

        except restaurant_details.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, 'restaurant/re_register.html')

    return render(request, 'restaurant/re_register.html')

def re_home(request):
    data = restaurant_order.objects.all()
    return render(request,'restaurant/re_home.html',{"data":data})

def stocks(request):
    data=restaurant_order.objects.all()
    return render(request,"restaurant/re_home.html")

def add_card(request):
    try:
        # Fetch the first registered restaurant with r_login=True
        reg = restaurant_details.objects.filter(r_login=True).first()

        # If no restaurant is logged in, redirect
        if not reg:
            return redirect('/re_home/')  # Corrected redirect location

        # Fetch food items/orders with f_login=True for the current client
        data = temp_table.objects.filter(client_id=reg.client_id, f_login=True)

        # Create a dictionary to track unique Br_id and their records
        br_id_map = {}
        for item in data:
            if item.Br_id not in br_id_map:
                br_id_map[item.Br_id] = []
            br_id_map[item.Br_id].append(item)

        # Identify and remove duplicate Br_id entries, keeping only one
        for br_id, items in br_id_map.items():
            if len(items) > 1:
                # Delete all but one of the duplicate records
                for item_to_delete in items[1:]:
                    item_to_delete.delete()

        # Convert dictionary values to a list of remaining unique records
        unique_data = [items[0] for items in br_id_map.values()]

        if request.method == "POST":
            # Extract the Br_id and quantity from the POST request
            br_id = request.POST.get('submit_quantity')
            quantity = int(request.POST.get(f'quantity_{br_id}'))

            # Update all items with the same Br_id
            items_to_update = temp_table.objects.filter(Br_id=br_id)
            for item in items_to_update:
                item.quantity = quantity
                item.Total_price = quantity * item.price
                item.save()

            # Redirect to avoid form resubmission issues
            return redirect('/add_card')

        # Get the first item to check payment status
        payment_info = temp_table.objects.filter(client_id=reg.client_id).first()

        context = {
            "data": unique_data,
            "pay": payment_info.payment_done if payment_info else False,  # Avoid None issues
        }

        return render(request, 'restaurant/add_card.html', context)

    except restaurant_details.DoesNotExist:
        # Redirect if no registered restaurant is found
        return redirect('/re_home/')

    except Exception as e:
        # Optionally log the exception or handle other errors
        print(f"An error occurred: {e}")
        return redirect('/re_home/')

def cart(request, Br_id):
    data = restaurant_order.objects.get(Br_id=Br_id)
    a = data.Br_id
    b = data.food_name
    c = data.image
    d = data.price
    reg = restaurant_details.objects.get(r_login=True)
    e = reg.client_id
    reg.total_done=True
    reg.save()


    cart = temp_table(Br_id=a, food_name=b, image=c, price=d, client_id=e)
    cart.f_login = True
    cart.save()
    messages.info(request, f"{cart.food_name} Added Successful")
    return redirect('/re_home/')
def process_payment(request):
    try:
        # Fetch the logged-in restaurant details
        restaurant = restaurant_details.objects.get(r_login=True)

        # Filter temp_table entries by the logged-in client's ID and f_login=True
        client_id = restaurant.client_id  # Assuming the client_id is stored in the restaurant_details
        total_price = temp_table.objects.filter(f_login=True, client_id=client_id).aggregate(Sum('Total_price'))['Total_price__sum'] or 0

        # Update the restaurant's full_amount and mark payment as done
        restaurant.full_amount = total_price
        restaurant.total_done = True
        restaurant.save()

        return render(request, 'restaurant/payments.html', {"data": restaurant})

    except restaurant_details.DoesNotExist:
        # Handle the case where the restaurant details are not found
        return render(request, 'restaurant/payments.html', {"error": "Restaurant details not found."})

def payment(request):
    # Fetch the logged-in restaurant details
    data = restaurant_details.objects.get(r_login=True)
    a=data.client_id
    data.payment_done = True
    data.save()
    res=restaurant_details.objects.get(r_login=True,payment_done=True)
    id=res.client_id

    # Fetch the items in the cart
    total_items = temp_table.objects.filter(client_id=id)




    if request.method == 'POST':
        # Initialize item details string
        item_details = ""
        # Iterate over each item to compile the order details
        for item in total_items:
            total_price = item.price * item.quantity
            item_details += f"""
            Food ID: {item.Br_id}
            Food Item: {item.food_name}
            Price: Rs {item.price} per unit
            Quantity: {item.quantity}
            Total for this item: Rs {total_price}

            """

        # Email subject and body
        subject = f"Restaurant Order: {data.shop_name} - Food Supply Order Confirmation"
        plain_message = f"""
        Dear {data.name.capitalize()},
        Thank you for choosing our warehouse for your food supply needs!
        We are pleased to inform you that your order has been successfully placed. Below are the details of your order:
        {item_details}
        Your order will be processed and delivered to your restaurant as per the schedule. Please ensure that someone is available to receive the delivery.
        Thank you for your trust in our services. We look forward to serving you with the best quality food supplies.

        Best regards,
        Warehouse Team
        """

        # Send the email
        send_mail(subject, plain_message, 'demosample47@gmail.com', [data.email], fail_silently=False)




        # Mark each item in the cart as paid
        for item in total_items:
            item.payment_done = True
            item.save()

        messages.info(request, f"{data.client_id}: Payment Is Successful")
        return redirect('/re_home/')

    return render(request, 'payment.html')

def delete_item(request,item_id):
    item = temp_table.objects.filter(Br_id=item_id)
    item.delete()
    messages.success(request, 'Item deleted successfully.')
    return redirect('/add_card/')

def order_details(request):
    try:
        item = restaurant_details.objects.get(payment_done=True, r_login=True)


        data = temp_table.objects.filter(client_id=item.client_id)
        if data.exists():
            return render(request, 'restaurant/restaunt_details.html', {'data': data})
        else:
            return render(request, 'restaurant/restaunt_details.html')

    except restaurant_details.DoesNotExist:

        return render(request, 'restaurant/restaunt_details.html')

def res_logout(request):

    data = restaurant_details.objects.get(r_login=True)
    data.r_login = False

    data.save()
    messages.success(request, 'Restaurant Logout Is Successful')

    return redirect('/')

