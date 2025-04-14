# 💻 Laptop Webstore – Cloud-Hosted E-commerce Platform

This project is a fully functional **e-commerce web application** that allows users to **browse, filter, and purchase laptops**. It features **session-based authentication** implemented using Flask and dynamic content rendering via **Jinja2** for an interactive and responsive user experience.

The webstore is hosted on a **Linux virtual machine** in **Google Cloud Platform**, using **Nginx** as a production web server. This setup was chosen to ensure **24/7 service availability**, low latency, and **basic security** suitable for demonstration purposes.

> ⚠️ **Note:**  
> The code available in this repository is a local development version used in **Visual Studio Code**. For security reasons, the hosted version differs slightly, and **sensitive configurations (e.g., production credentials and database connections)** have been excluded.

---

## 🔧 Technical Decisions

- Originally, the database was built and tested using **SQL Server Management Studio**.
- During cloud migration, **MariaDB** was selected for compatibility with the Linux VM.
- Only minor **SQL syntax adjustments** were needed (e.g., date functions, auto-incrementing keys).
- Session handling, cart management, and login redirects are handled using **Flask** and **Jinja2**.
- **Nginx** was configured to proxy traffic to the Flask server and ensure reliable access.

---

## 🌐 Cloud Hosting Overview

- **Platform**: Google Cloud Compute Engine  
- **OS**: Debian-based Linux VM (e2-micro, Free Tier eligible)  
- **Web Server**: Nginx (serving Flask via proxy)  
- **Domain**: Currently accessible via static external IP  
- **Database**: MariaDB, hosted on the same instance  
- **Security**: Minimal configuration to reduce costs (IP whitelisting, basic firewall)

---

## ✅ Features

-  View laptop catalog with live stock and price
-  Filter and search for laptops by brand/category
-  Add to cart, update quantity, remove items
-  Submit orders with live stock checks
-  Session-based login/logout and user management
-  My account section for addresses and info
-  Admin-ready foundation for future extensions
