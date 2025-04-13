
from django.shortcuts import render,redirect
from django.contrib import messages
from admins.models import restaurant_details,restaurant_order,modules_registration,temp_table
from admins.crypto_utils import load_rsa_public_key,encrypt_message,generate_rsa_keys,load_rsa_private_key,generate_random_aes_key
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.core.files.base import ContentFile
from django.shortcuts import redirect
import random



def su_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        category = request.POST.get("category")



        # Check if the email address is a valid Gmail address
        if not email.endswith('@gmail.com'):
            messages.error(request, "Only Gmail addresses are allowed.")
            return render(request, 'sustainability/su_register.html')

        # Check if the email is unique
        if modules_registration.objects.filter(email=email).exists():
            messages.error(request, "This email address is already registered.")
            return render(request, 'sustainability/su_register.html')

        # Save the new registration
        obj = modules_registration(name=name, email=email, phone_number=phone, category=category)
        obj.save()

        messages.info(request, "Sustainability Registration Successful")
        return render(request, 'sustainability/su_register.html')



    return render(request,'sustainability/su_register.html')

def su_login(request):
    try:
        if request.method == "POST":
            print(1)
            email = request.POST.get('email')
            password = request.POST.get('password')
            print(2)
            users = modules_registration.objects.get(email=email, password=password)
            if users:
                users.su_login=True
                users.save()

                messages.info(request, "Sustainability Login Successful")
                print(5)
                return redirect('/su_home/')
            return render(request,'sustainability/su_register.html')
        return render(request, 'sustainability/su_register.html')
    except:

        return redirect('/su_login/')

def su_home(request):
    return render(request,'sustainability/su_home.html')

def order(request):
    return render(request, 'sustainability/order_details.html')





def su_encrypt(request):
    data = temp_table.objects.filter(payment_done=True)

    # Encrypt records that haven't been encrypted or decrypted
    for item in data:
        if not item.f_encrypt and not item.f_decrypt:
            item.dec_food_name = encrypt_message(str(item.food_name))
            item.dec_price = encrypt_message(str(item.price))
            item.dec_quantity = encrypt_message(str(item.quantity))
            item.dec_Total_price = encrypt_message(str(item.Total_price))
            item.f_encrypt = True
            item.f_decrypt = False
            item.save()

    # Extract unique client IDs
    client_ids = data.values_list('client_id', flat=True).distinct()

    context = {
        'data': data,
        'client_ids': client_ids
    }

    return render(request, "sustainability/order_details.html", context)




def f_getkey(request, id):
    try:
        logged_in_user = modules_registration.objects.filter(su_login=True).first()
    except modules_registration.DoesNotExist:
        messages.error(request, "No logged-in user found.")
        return redirect('/su_encrypt/')

    try:
        temp_table_records = temp_table.objects.filter(client_id=id)
        if not temp_table_records.exists():
            raise temp_table.DoesNotExist
    except temp_table.DoesNotExist:
        messages.error(request, "Record not found.")
        return redirect('/encrypt/')

    # Load and export the private key
    private_key = generate_random_aes_key()

    # Save the base64-encoded key in each record
    for record in temp_table_records:
        record.f_key = private_key
        record.save()

    # Send the base64-encoded key via email
    send_mail(
        f"{logged_in_user.category} Decryption Key",
        'Hi {0},\nYour decryption key is:\n\n{1}\n\nKindly use this key to decrypt the records.\n\nThank you.'.format(
            logged_in_user.name, private_key),
        'vetrim.surya@gmail.com',
        [logged_in_user.email],
        fail_silently=False,
    )

    # Mark the key as sent for each record
    for record in temp_table_records:
        record.f_getkey = True
        record.save()

    messages.info(request, f"Decryption key sent successfully.")
    return redirect('/su_home/')


def f_check_key(request, id):
    # Retrieve the queryset based on client_id
    d = temp_table.objects.filter(client_id=id)
    print(d)

    if not d.exists():
        messages.error(request, "No record found for the given client ID.")
        return redirect('/su_home/')

    if request.method == "POST":
        keyenter = request.POST.get('keyenter')

        # Iterate through the queryset and update each record
    for record in d:
        record.f_keyenter = keyenter
        record.save()

    for data in d:
        if data.f_key == keyenter:
            data.f_keycheck = True
            data.f_encrypt = False
            data.f_decrypt = True
            data.save()

        else:
            messages.error(request, 'Wrong Key')
    verified= temp_table.objects.filter(f_keycheck=True)
    if verified:
        messages.info(request,"Key verified successfully")
        return redirect('/su_encrypt/')
    else:
        return redirect('/encrypt/')


def su_analyze(request):
    data = temp_table.objects.filter(f_decrypt=True)
    return render(request,'sustainability/su_analyze.html',{'data':data})



from sklearn.ensemble import RandomForestClassifier

def su_calculate(request, id):
    try:
        # Load data
        df = pd.read_csv('C:/Users/ar900/OneDrive/Desktop/foodsupplychain/FoodSupplyChain/FoodSupplyChain/Foodsupplychain/dataset/sustainability/sustainability.csv')

        # Debugging: Check column names in df
        print(f"Columns in df: {df.columns.tolist()}")

        # Expected column names
        required_columns = {'item', 'carbon_footprint_(kgco2e)', 'water_usage_(liters)', 'energy_consumption_(kwh)'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise KeyError(f"Missing columns in the DataFrame: {', '.join(missing_columns)}")

        # Features and target variables
        features = df[['carbon_footprint_(kgco2e)', 'water_usage_(liters)', 'energy_consumption_(kwh)']]
        target = df['item']

        # Encode categorical target variable
        le_item = LabelEncoder()
        target_encoded = le_item.fit_transform(target)

        # Initialize Random Forest Classifier
        n_estimators = 100
        rf = RandomForestClassifier(n_estimators=n_estimators, random_state=42)

        # Fit the model
        rf.fit(features, target_encoded)

        # Retrieve specific records from temp_table
        data_list = temp_table.objects.filter(client_id=id)

        # Process each record
        for data in data_list:
            input_data = {
                'item': data.food_name,  # Match casing to your dataset
            }
            print(f"Input data: {input_data}")

            # Get features for the input item
            input_features = df[df['item'] == data.food_name][
                ['carbon_footprint_(kgco2e)', 'water_usage_(liters)', 'energy_consumption_(kwh)']]

            if input_features.empty:
                messages.error(request, f"Input data for {data.food_name} does not match training data.")
                continue  # Skip to the next record

            # Prepare input feature for prediction
            input_features_for_prediction = input_features.mean().values.reshape(1, -1)

            # Predict the encoded item value using classification
            input_prediction_encoded = rf.predict(input_features_for_prediction)
            input_prediction_encoded = input_prediction_encoded[0]

            # Decode the predicted value to get the item name
            input_item = le_item.inverse_transform([input_prediction_encoded])[0]
            print(f"Predicted item: {input_item}")

            # Find records matching the predicted item
            cluster_data = df[df['item'] == input_item]
            print(f"Cluster data: {cluster_data}")

            # Update the temp_table instance with the predicted item info
            if not cluster_data.empty:
                data.Carbon_Footprint = cluster_data['carbon_footprint_(kgco2e)'].mean()
                data.Water_Usage = cluster_data['water_usage_(liters)'].mean()
                data.Energy_Consumption = cluster_data['energy_consumption_(kwh)'].mean()
                data.su_done = True
                data.status = "Sustainability Analysis Done"
                data.save()

                # Provide feedback for each record
                messages.info(request, f"{data.client_id}: Sustainability Analysis Successfully Completed for {data.food_name}")
            else:
                messages.error(request, f"Predicted item for {data.food_name} not found in the dataset.")

    except Exception as e:
        # Handle any unexpected errors
        print(f"An error occurred: {e}")
        messages.error(request, "An unexpected error occurred during sustainability analysis.")

    return redirect('/su_analyze/')

def su_report(request):
    data=temp_table.objects.filter(su_done=True)
    return render(request,"sustainability/su_report.html",{'data':data})


def generate_pdf(request, id):
    # Retrieve queryset of temp_table objects or return 404 if not found
    try:
        users = temp_table.objects.filter(client_id=id)
        reg = restaurant_details.objects.get(client_id=id)
        if not users.exists():
            raise Http404("No records found for the specified client ID.")
    except temp_table.DoesNotExist:
        raise Http404("Records not found")

    title = "Comprehensive Restaurant and Food Supply Chain Solutions for Efficient Operations and Sustainability"
    project_id = f"Restaurant ID: {id}"

    # Prepare content for the PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    # Custom styles
    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.red,  # Title color changed to red
        alignment=1,  # Center alignment
        spaceAfter=12  # Space below title
    )
    style_project_id = ParagraphStyle(
        'ProjectID',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.black,  # Project ID color changed to red
        alignment=1,  # Center alignment
        spaceAfter=12  # Space below project ID
    )
    style_section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.red,  # Section heading color changed to red
        alignment=0,  # Left alignment
        spaceAfter=12  # Space below section headings
    )
    style_table_space = ParagraphStyle(
        'TableSpace',
        parent=styles['Normal'],
        spaceBefore=15  # Space before each table
    )
    style_normal = styles['Normal']

    # Title and Project ID
    title_paragraph = Paragraph(title, style_title)
    project_id_paragraph = Paragraph(project_id, style_project_id)
    elements = [title_paragraph, project_id_paragraph]

    # Helper function to create tables
    def create_table(data):
        table = Table(data, colWidths=[6 * cm, 10 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),  # Table header background changed to red
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color is white
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align Field and Value content to the center
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ]))
        return table

    # Iterate over each user in the queryset and add their data to the PDF
    for user in users:
        sustainability_report_data = [
            ["Field", "Value"],
            ["Project ID:", user.Br_id],
            ["Food Name:", user.food_name],
            ["Carbon Footprint (kg CO2e):", user.Carbon_Footprint],
            ["Water Usage (liters):", user.Water_Usage],
            ["Energy Consumption (kWh):", user.Energy_Consumption],
        ]

        section_heading = Paragraph(f"SUSTAINABILITY REPORT FOR {user.Br_id}:", style_section_heading)
        elements.append(section_heading)
        elements.append(create_table(sustainability_report_data))
        elements.append(Paragraph("", style_table_space))  # Add extra space before the next table

    # Build the PDF
    doc.build(elements)

    pdf_data = buffer.getvalue()
    buffer.close()

    # Prepare HTTP response with PDF data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{title}_{id}.pdf"'
    response.write(pdf_data)

    # Save PDF file to the model field
    for user in users:
        user.f_report.save(f"{title}_{user.Br_id}.pdf", ContentFile(pdf_data))
        user.fview = True
        user.save()
    reg.s_report.save(f"{title}.pdf", ContentFile(pdf_data))
    reg.pdf_done = True
    reg.dl_approve = False
    reg.dl_reject = False
    reg.f_approve = False
    reg.f_reject = False
    reg.save()

    messages.info(request, f"{id}: Sustainability Report Generated Successfully")

    # Redirect after generating PDF
    return redirect('/su_report/')


def su_logout(request):
    messages.info(request,"Sustainability Logout Successful")
    return redirect('/')


def encrypt(request):
    # Fetch all records with payment done
    data = temp_table.objects.filter(payment_done=True)

    # Get distinct client IDs from the filtered data
    client_ids = data.values_list('client_id', flat=True).distinct()

    # Fetch the first record where f_getkey is True and payment is done
    getkey = data.filter(f_getkey=True).first()

    # Fetch the first record where f_keycheck is True
    keycheck = temp_table.objects.filter(f_keycheck=True).first()

    # Prepare the context to pass to the template
    context = {
        'data': data,
        'client_ids': client_ids,
        'getkey': getkey,
        'keycheck': keycheck,
    }

    # Render the template with the context
    return render(request, 'sustainability/encrypt.html', context)
def s_analyze(request):
    data = temp_table.objects.filter(f_decrypt=True)
    client_ids = data.values_list('client_id', flat=True).distinct()
    sudone=temp_table.objects.filter(su_done=True).first()
    context = {
        'data': data,
        'client_ids': client_ids,
        'sudone':sudone



    }
    return render(request,'sustainability/s_analyze.html',context)

def report(request):
    data = temp_table.objects.filter(su_done=True)
    client_ids = data.values_list('client_id', flat=True).distinct()
    view = temp_table.objects.filter(su_done=True).first()
    context = {
        'data': data,
        'client_ids': client_ids,
        'view':view


    }

    return render(request, 'sustainability/report.html', context)
