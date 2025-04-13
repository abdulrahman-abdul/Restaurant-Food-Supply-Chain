from django.shortcuts import render,redirect
from django.contrib import messages
from admins.models import restaurant_details,restaurant_order,modules_registration,temp_table
from django.core.mail import send_mail
import random
# from reportlab.lib.colors import red, black
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
def home(request):
    return render(request,'home/home.html')

def admin_login(request):
    admin_page = {"admin@gmail.com": "Admin"}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('Password')
        try:
            if admin_page.get(email) == password:
                messages.info(request, "Admin Login Successful")
                return render(request, "admin/admin_home.html")
            else:
                return redirect('/admin_login/')
        except Exception as e:

            return redirect('/admin_login/')
    return render(request,'admin/admin_login.html')

def admin_home(request):
    return render(request,'admin/admin_home.html')

def restaurants_details(request):
    data = restaurant_details.objects.all()
    return render(request, "restaurant/manage_log1.html", {'data': data})

def delivery_details(request):
    data = modules_registration.objects.filter(category='Delivery')
    return render(request, "delivery/manage_log2.html", {'data': data})

def sustainability_details(request):
    data = modules_registration.objects.filter(category='Sustainability')
    return render(request, "sustainability/manage_log3.html", {'data': data})

def approve(request,id):
    try:
        client = modules_registration.objects.get(id=id)

        d= random.randint(10000,99999)
        client.password = d


        subject = f"{client.category}:your username and your password"
        plain_message = f"Hi,\n\nThank you for using this web application,\n\n Your username is {client.email} and Your password is: {client.password}.\n\nSo kindly use this username and  password while login into the portal of {client.category} process.\n\nThank you"

        send_mail(subject, plain_message, 'demosample47@gmail.com', [client.email], fail_silently=False)

        r= random.randint(1000,9999)
        client.client_id=f"FS:{r}"

        client.approve = True
        client.save()
        messages.info(request,f"{client.client_id}: Registration Approved Successfully")
        return redirect('/admin_home/')
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
        return redirect('/admin_home/')

def rejection(request,id):
    try:
        client = modules_registration.objects.get(id=id)


        subject = 'Rejection Notification'
        plain_message = f"Hi {client.name},\n\nYour request for {client.category} has been rejected.\n\n Sorry we could not move forward your {client.category}\n\nThank you."
        send_mail(subject, plain_message, 'sender@example.com', [client.email], fail_silently=False)

        # Update client status or other fields related to rejection
        client.reject = True  # Assuming 'reject' is a field in your Brine model
        client.save()

        messages.info(request,"Registration rejected")

        return redirect('/admin_home/')  # Redirect to the admin page after rejection
    except Exception as e:
        # Print the exception for debugging purposes
        print(f"An error occurred while sending rejection email: {e}")
        return redirect('/admin_home/')

def r_approve(request,id):
    try:
        client = restaurant_details.objects.get(id=id)
        d= random.randint(10000,99999)
        client.password = d


        subject = "Restaurant:your username and your password"
        plain_message = f"Hi,\n\nThank you for using this web application,\n\n Your username is {client.email} and Your password is: {client.password}.\n\nSo kindly use this username and  password while login into the portal of Restaurant process.\n\nThank you"

        send_mail(subject, plain_message, 'demosample47@gmail.com', [client.email], fail_silently=False)

        r= random.randint(1000,9999)
        client.client_id=f"FS:{r}"

        client.r_approve = True
        client.save()
        messages.info(request,f"{client.client_id}: Registration Approved Successfully")
        return redirect('/admin_home/')
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
        return redirect('/admin_home/')

def r_rejection(request,id):
    try:
        client = restaurant_details.objects.get(id=id)

        subject = 'Rejection Notification'
        plain_message = f"Hi {client.name},\n\nYour request for Restaurant has been rejected.\n\n Sorry we could not move forward your Restaurant\n\nThank you."
        send_mail(subject, plain_message, 'sender@example.com', [client.email], fail_silently=False)

        # Update client status or other fields related to rejection
        client.r_reject = True  # Assuming 'reject' is a field in your Brine model
        client.save()
        messages.info(request,"Registration rejected")

        return redirect('/admin_home/')  # Redirect to the admin page after rejection
    except Exception as e:
        # Print the exception for debugging purposes
        print(f"An error occurred while sending rejection email: {e}")
        return redirect('/admin_home/')

def upload_stock(request):
    if request.method == "POST":
        try:
            # Retrieve form data
            food_item = request.POST["food_item"]
            price = float(request.POST["food_price"])
            image = request.FILES["food_image"]

            # Validate price
            if price <= 0:
                messages.error(request, "Price must be a positive number.")
                return render(request, 'admin/upload_stock.html')

            # Create and save the Food object
            obj = restaurant_order(food_name=food_item, price=price, image=image)
            obj.Br_id = f"FD:{random.randint(1000, 9999)}"
            obj.save()
            messages.success(request, f"{obj.Br_id}: FoodItems Uploaded Successfully")

        except ValueError:
            messages.error(request, "Invalid input: please enter numeric values for price.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('admin_home')  # Redirect to admin home page after successful upload

    return render(request, 'admin/upload_stock.html')

def warehouse_stock(request):
    data=restaurant_order.objects.all()
    return render(request,'admin/warehouse.html',{"data":data})


def sus_report(request):
    data=restaurant_details.objects.filter(pdf_done=True,dl_approve=True)
    return render(request,'admin/sus_report.html',{"data":data})

def admin_logout(request):
    messages.info(request, "Admin Logout Successful")
    return redirect('/')

def f_approve(request, id):
    try:
        # Fetch restaurant details based on the provided client ID
        data = restaurant_details.objects.get(id=id)
        client_id = data.client_id

        # Retrieve all items associated with the specific client ID
        total_items = temp_table.objects.filter(client_id=client_id)

        # Initialize the string to hold item details
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
        subject = f"Restaurant Order Delivered: {data.shop_name} - Food Supply Delivery Confirmation"
        plain_message = f"""
        Dear {data.name.capitalize()},
        We are pleased to inform you that your order has been successfully delivered! Below are the details of your delivery:
        {item_details}
        Thank you for your business.

        Best regards,
        Warehouse Team
        """

        # Send the email notification
        send_mail(subject, plain_message, 'demosample47@gmail.com', [data.email], fail_silently=False)

        # Update the order status
        data.f_approve = True
        data.f_reject = False
        data.save()

        # Optionally, delete all records in temp_table (if intended)
        temp_table.objects.all().delete()

        # Show a success message and redirect to the admin home page
        messages.info(request, f"{data.client_id}: Order Delivered Successfully")
        return redirect('/admin_home/')

    except restaurant_details.DoesNotExist:
        # Handle the case where the client ID does not exist
        messages.error(request, "The specified restaurant does not exist.")
        return redirect('/admin_home/')
    except Exception as e:
        # Handle other potential errors
        print(f"An error occurred: {e}")
        messages.error(request, "An error occurred while processing the order.")
        return redirect('/admin_home/')

    # Render the admin home template if the request method is not POST
    return render(request, 'admin/admin_home.html')

def f_reject(request,id):
    try:
        print(1)
        # Retrieve the client and associated sustainability module registration
        client = restaurant_details.objects.get(id=id)
        reg = modules_registration.objects.filter(category='Delivery').first()
        print(2)

        if reg:  # Check if a sustainability registration exists
            reg.dl_client_id = id
            reg.save()
            print(3)


            data = modules_registration.objects.get(dl_client_id=id)
            print(4)

            # Prepare the email content
            subject = 'Sustainability Rejection Notification'
            plain_message = (
                f"Hi Delivery Team,\n\n"
                "We regret to inform you that your delivery request has been rejected.\n\n"
                "The sustainability aspects of your food have not met our evaluation criteria. Please review and reanalyze your submission to ensure it aligns with our standards.\n\n"
                "Thank you for your understanding and cooperation."
            )
            send_mail(subject, plain_message, 'sender@example.com', [data.email], fail_silently=False)
            print(5)

        # Update the client's status to reflect the rejection
        client.f_reject = True  # Assuming 'dl_reject' is a field in your restaurant_details model
        client.f_approve = False
        client.dl_approve=False
        client.save()
        print(6)

        # Notify the user of the rejection
        messages.info(request, "The delivery process has been rejected.")

        # Redirect to the delivery home page after rejection
        return redirect('/admin_home/')
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"An error occurred while sending the rejection email: {e}")
        return redirect('/admin_home/')