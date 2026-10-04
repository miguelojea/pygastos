# pyGastos

Proyecto para automatizar el registro de ingresos y gastos en bases de datos.

Loas entradas se registrarán automáticamente enviando por un formulario web:

* CSVs
* PDFs
* Información de algún gasto. Útil para cuando se pague en efectivo.

## Planificación

Partes:

* [ ] Acceso a base de datos en modo admin - Python + sqlite_web.
* [ ] Inicio de sesión y otras seguridades. - Python + Flask.
* [ ] Abrir a la red externa.
* [ ] Ingreso de datos en DB - Python + SQLite.
* [ ] Web para ingrsar datos manuales - HTML + CSS + JS
* [ ] Web para ingresar datos automáticos (CSV / PDF) - HTML + CSS + JS
* [ ] Backend para recibir y procesar datos manuales. - Python + Flask
* [ ] Backend para recibir y procesar datos automáticos. - Python + Flask
* [ ] Rutina para exportar DB a hoja de Google Sheets. - Python + Google Sheets.
* [ ] CI/CD con Jenkins.

## Documentación

Activar sqlite-web:

python -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 5001

## Features y más info

## TODOs futuros:

- [ ] Añadir también notas complementarias en cualquier momento (desde el móvil, a través de otro formulario web), para ayudar a completar la información de los archivos.
  - [ ] La interacciónm con las bases de datos será solo accesible desde red local, mientras que lo de añadir notas será accesible desde la red pública.
- [ ] Rutina para volcar datos a hojas de Excel / Google Sheets.
- [ ] Jenkins pipeline da OK aunque los scripts de deploy no funcionen. Por ejemplo main.py falla porque falta alguna dependencia. No se reporta de ninguna forma, tal vez por ser un script iniciado en segundo plano.

## Otras dependencias

## Otros

### Estructura dependencias:

Librerías:

* Pdf_parser
* Csv_parser
* Excel_Generator
*

---
