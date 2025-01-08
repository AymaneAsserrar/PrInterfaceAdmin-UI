# Utiliser l'image Python 3.12 Alpine comme base
FROM python:3.12-alpine

# Définir l'environnement pour éviter les invites interactives
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Installer les dépendances système nécessaires
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt /app/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copier le reste de l'application dans le conteneur
COPY app.py /app

# Définir la commande par défaut pour démarrer l'application
CMD ["python", "app.py"]