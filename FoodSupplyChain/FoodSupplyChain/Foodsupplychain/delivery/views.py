from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from django.contrib import messages
from admins.models import restaurant_details,restaurant_order,modules_registration,temp_table
from django.core.mail import send_mail
import random


def dl_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        category = request.POST.get("category")


        # Check if the email address is a valid Gmail address
        if not email.endswith('@gmail.com'):
            messages.error(request, "Only Gmail addresses are allowed.")
            return render(request, 'delivery/dl_register.html')

        # Check if the email is unique
        if modules_registration.objects.filter(email=email).exists():
            messages.error(request, "This email address is already registered.")
            return render(request, 'delivery/dl_register.html')

        # Save the new registration
        obj = modules_registration(name=name, email=email, phone_number=phone, category=category)
        obj.save()
        messages.info(request, "Delivery Registration Successful")
        return render(request, 'delivery/dl_register.html')



    return render(request,'delivery/dl_register.html')

def dl_login(request):
    try:
        if request.method == "POST":
            print(1)
            email = request.POST.get('email')
            password = request.POST.get('password')
            print(2)
            users = modules_registration.objects.get(email=email, password=password)
            if users:
                users.dl_login=True
                users.save()


                messages.info(request, "Delivery Login Successful")
                print(5)
                return redirect('/dl_home/')
            return render(request,'delivery/dl_register.html')
        return render(request, 'delivery/dl_register.html')
    except:

        return redirect('/dl_login/')

def dl_home(request):
    return render(request,'delivery/dl_home.html')

def DEl_report(request):
    data = temp_table.objects.filter(su_done=True,fview=True)
    client_ids = data.values_list('client_id', flat=True).distinct()
    view = temp_table.objects.filter(su_done=True,fview=True).first()# No need to filter again, reuse the filtered data

    context = {
        'data': data,
        'client_ids': client_ids,
        'view': view
    }

    return render(request, 'delivery/DEL_report.html', context)

def Su_report(request):
    data = temp_table.objects.filter(su_done=True)
    return render(request,'delivery/Dl_report.html',{'data':data})


def delivery_process(request):
    # Get the restaurant details where payment is done
    data = restaurant_details.objects.filter(payment_done=True)

    # Get temp table entries where fview is True
    reg = temp_table.objects.filter(fview=True)

    # Convert temp_table QuerySet to a set of client_ids for quick lookup
    reg_client_ids = set(reg.values_list('client_id', flat=True))

    # Filter the data to only include items where client_id is in reg_client_ids
    filtered_data = data.filter(client_id__in=reg_client_ids)

    # Render the template with the filtered data
    return render(request, 'delivery/delivery.html', {'data': filtered_data})

def order(request,id):
    data= restaurant_details.objects.get(id=id)
    a=data.client_id
    reg=temp_table.objects.filter(client_id=a)
    return render(request, 'delivery/order.html', {'data': reg})

def dl_logout(request):
    messages.info(request, "Delivery Logout Successful")
    return redirect('/')

def dl_approve(request,id):
    client = restaurant_details.objects.get(id=id)
    client.dl_approve=True
    client.dl_reject =False
    client.save()
    messages.info(request, f"{client.client_id}:Delivery Approved Successfully")
    return redirect('/dl_home/')


def dl_reject(request, id):
    try:
        # Retrieve the client and associated sustainability module registration
        client = restaurant_details.objects.get(id=id)
        reg = modules_registration.objects.filter(category='Sustainability').first()

        if reg:  # Check if a sustainability registration exists
            reg.su_client_id = id
            reg.save()

            # Retrieve the updated registration data
            data = modules_registration.objects.get(su_client_id=id)

            # Prepare the email content
            subject = 'Sustainability Rejection Notification'
            plain_message = (
                f"Hi Sustainability Team,\n\n"
                "We regret to inform you that your delivery request has been rejected.\n\n"
                "The sustainability aspects of your food have not met our evaluation criteria. "
                "Please review and reanalyze your submission to ensure it aligns with our standards.\n\n"
                "Thank you for your understanding and cooperation."
            )
            send_mail(subject, plain_message, 'sender@example.com', [data.email], fail_silently=False)

        # Update the client's status to reflect the rejection
        client.dl_reject = True
        client.dl_approve = False
        client.save()

        # Update the su_done field in temp_table for the specific client_id
        e = client.client_id
        data = temp_table.objects.filter(client_id=e)

        for i in data:

            i.su_done = 0
            i.fview=0
            i.save()

        # Notify the user of the rejection
        messages.info(request, "The delivery process has been rejected.")

        # Redirect to the delivery home page after rejection
        return redirect('/dl_home/')
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"An error occurred while sending the rejection email: {e}")
        messages.error(request, "An error occurred while processing the rejection.")
        return redirect('/dl_home/')