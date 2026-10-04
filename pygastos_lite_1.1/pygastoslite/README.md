# pyGastosLite

## Getting started

Web to add incomes and expenses to Google Sheets with Python + Flask.

## TODOs:

- [ ] Tab to add notes. E.g. I pay something by card but the concept on the bank app will not be intuitive, so a note is added. Or add directly the entry?
- [ ] Tests
- [ ] CI/CD GitLAB + Jenkins
- [ ] Undo last entry added. To do so, set last updated entry info after any add.
- [X] logging (file + console)

No Lite:

* Usar Base de datos.
* Cuando se quiera editar en manual, generar un libro de Google Sheets a partir de una plantilla de Google Sheets y la base de datos.
* Al terminar de editar el libro de Google Sheets, se comparará con la base de datos y esta se actualizará.
* O si no usar una misma Sheet pero que se elimine y reescriba todo el contenido cada vez que se quiera usar. Para evitar tener que crear nuevas hojas, dar permisos, etc.

### Security

- [X] Basic security to make public -> Password + WSGI (gunicorn)
- [X] Nginx (proxy inverso)
- [X] Hash password
- [ ] HTTPS

## **Seguridad adicional**

* No uses `app.run(...)` para producción. Usa un servidor WSGI como gunicorn.
* **HTTPS obligatorio**: Delante del servidor WSGI, usa un proxy reverso (como NGINX con Let's Encrypt) si expones el servidor públicamente.
* **Variables sensibles** en `.env` + `python-dotenv` (por ejemplo, la clave secreta).
* **Hashea las contraseñas**: Usa `werkzeug.security.generate_password_hash()` para generar los hash que guardas.
* Mejora app.secret_key para producción.

Esto sigue siendo inseguro frente a fuerza bruta si alguien cambia IPs constantemente. Si quisieras robustecer más:

* Usar CAPTCHA tras X intentos.
* Bloquear IPs a nivel de proxy o nginx.
* Hacer login con token único para ti (más difícil de adivinar).

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

---

# Link with Google Sheets Workbook

1. Create service account: [https://console.cloud.google.com/apis/api/sheets.googleapis.com/credentials](https://console.cloud.google.com/apis/api/sheets.googleapis.com/credentials)
2. Get the credential json from  the created service account: Select desired account -> Keys -> Add key -> Json will be downloaded. Add them to private\credentials.json.
3. Share the Google Sheets Workbook with the service account.
4. Use the Workbook id in the project. E.g. In the following Workbook URL, the ID is the bold characters: https://docs.google.com/spreadsheets/d/**1AI_f9J6vV0sYp65XkeKzFYMdsZYzB0jCaLKatTbzKJE**/edit?gid=768902382#gid=768902382

## 3333

4444
