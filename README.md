# Quizzong

Quizzong is a Django-based quiz web application. Follow the steps below to set up the project on your local machine.

## Prerequisites

Ensure the following are installed on your system:

- Python 3.8+
- pip
- PostgreSQL
- Git
- Virtualenv

---

## Setup Instructions

### 1. Clone the Project

Open your terminal or command prompt and run:

```sh
git clone https://github.com/jungnarph/Quizzong.git
```
```sh
cd Quizzong
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment:

```sh
python -m venv .venv
```
```sh
.venv\Scripts\activate
```

### 3. Installed Required Dependencies

Once your virtual environment is activated, install the required packages listed in the requirements.txt file:

```sh
pip install -r requirements.txt
```

### 4. Set Up Your PostgreSQL Database

Ensure PostgreSQL is installed and running on your system. Open your command prompt and login your credentials. Then, create a database using the following command (adjust the username accordingly):

```sh
psql -U postgres
```
```sh
CREATE DATABASE your-database-name;
```

### 5. Configure Environment Variables

Create a .env file in the root of your project directory. This file will store your secret keys and configuration settings securely. Copy the provided example environment file to a new .env file:

```sh
cp .env.example .env
```

### 6. Run the following commands to apply migrations and create a superuser for the Django admin:

```sh
python manage.py migrate
```
```sh
python manage.py createsuperuser
```

### 7. Start the Development Server

Finally, start the Django development server:

```sh
python manage.py runserver
```

### 8. Open the Development Server

Open your browser and navigate to http://127.0.0.1:8000.

