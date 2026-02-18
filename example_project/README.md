## Setting Up The Example Project

Here's how to get the example project up and running:

### 1. Clone the Repository:

```bash
git clone https://github.com/AlexIvanchyk/django-localekit.git
cd django-localekit/example_project
```

### 2. Install Dependencies:

**Option A — from the example project (recommended):**

```bash
cd example_project
poetry install
```

This installs Django, Django REST Framework, and django-localekit from the parent directory (editable). Then run all commands below with `poetry run` or activate the env with `poetry shell`.

**Option B — from the repository root:**

```bash
poetry install
cd example_project
```

Use the root virtualenv for the rest of the steps (then you can run `python manage.py` without `poetry run`).

### 3. Set Up Database:

From the `example_project` directory, run the migrations (use `poetry run` if you installed with Option A):

```bash
poetry run python manage.py migrate
```

### 4. Load Sample Data (Optional):

```bash
poetry run python manage.py loaddata initial_data.json
```

### 5. Collect static files (optional):

```bash
poetry run python manage.py collectstatic
```

### 6. Create Superuser:

```bash
poetry run python manage.py createsuperuser
```

Follow the prompts to create the user.

### 7. Run Development Server:

```bash
poetry run python manage.py runserver
```

Open your browser and go to `http://127.0.0.1:8000/` to see the project in action. Log in to the admin site at `http://127.0.0.1:8000/admin/` using the superuser credentials you created.
