FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo "Generating .env template" \
    && echo "# Auto-generated - do NOT commit" > .env \
    && echo "DB_PASSWORD=schoolspass" >> .env

CMD ["sh", "-c", "if [ ! -f .env ]; then echo 'Generating new .env file'; sed 's/schoolspass/$(openssl rand -hex 16)/' .env > .env.tmp && mv .env.tmp .env; fi && waitress-serve --listen=*:80 api:app"]
