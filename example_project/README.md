## Setting Up The Example Project

Here's how to get the example project up and running:

### 1. Clone the Repository:

```bash
git clone https://github.com/AlexIvanchyk/django_restful_translator.git
cd django_restful_translator/example_project
```

### 2. Install Dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up Database:

First, make sure you have your database configured. Then, run the migrations:

```bash
python manage.py migrate
```

### 4. Load Sample Data (Optional):

To populate your database with sample data:

```bash
python manage.py loaddata initial_data.json
```

### 5. Collects static files:

```bash
python manage.py collectstatic
```

### 6. Create Superuser:

To create an admin user:

```bash
python manage.py createsuperuser
```

Follow the prompts to create the user.

### 7. Run Development Server:

Now you're ready to run the development server:

```bash
python manage.py runserver
```

Open your browser and go to `http://127.0.0.1:8000/` to see the project in action. Log in to the admin site at `http://127.0.0.1:8000/admin/` using the superuser credentials you created.
