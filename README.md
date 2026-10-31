# 🩸 RaktSetu - Blood Donor Finder

RaktSetu (Setu means bridge) is a web application that connects people who need blood with people willing to donate it. Users can search donors by blood group and city, register as a donor, post blood requests with urgency, and contact donors while keeping phone numbers private.

This is a college mini project.

## Features

- **Home page** with hero slider, quick donor search, blood group cards, live statistics and blood donation awareness
- **Find Donor**: search by blood group and city, available donors are listed first
- **Donor Registration**: name, age, gender, blood group, phone, city, email, last donation date, availability
- **Request Blood**: patient, blood group, hospital, location, units, contact number, urgency (Normal / Urgent / Emergency)
- **Blood Requests**: active requests sorted by urgency, with a "Mark fulfilled" option
- **Statistics**: total donors, total requests, successful connections, blood groups available, donors per blood group
- **Donor Profile**: basic details, location and availability status
- **Contact Donor**: phone number stays masked until the person confirms they need blood, then Call and WhatsApp buttons appear
- **About Us**: purpose, how it works and blood donation basics
- **Responsive design** for mobile, tablet and desktop

## Smart rules

- A donor is shown as **Available** only if they marked themselves available **and** their last donation was at least **90 days** ago
- Duplicate phone numbers are not allowed
- All forms are validated in the browser (Bootstrap) and again on the server (Flask)


Your Name - BSc Computer Science mini project

https://raktsute-1.onrender.com/
