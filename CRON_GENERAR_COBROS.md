# Cron de facturación mensual (`generar_cobros`)

Instrucciones para programar en el servidor Oracle Cloud la ejecución mensual del
comando `generar_cobros`, que genera los cobros del período y evalúa los cortes
de servicio. Esto se hace fuera de Railway porque Railway no expone acceso a
`crontab` sobre el contenedor de la app — se necesita una máquina con acceso a
`cron` real, como el servidor Oracle.

## Requisitos previos en el servidor Oracle

- El repo del backend clonado en el servidor (por ejemplo en
  `/opt/gestionaguaApp` o la ruta que ya uses para desplegarlo).
- Un entorno virtual con las dependencias instaladas (`requirements.txt`).
- Acceso a la misma base de datos PostgreSQL de producción (variables de
  entorno `DB_*` configuradas en el `.env` de ese servidor, igual que en
  Railway).
- `DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production`.
- Variables `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD` en el `.env` del
  servidor para las alertas por correo si el comando falla (ver
  [Alertas por correo si el comando falla](#alertas-por-correo-si-el-comando-falla)).

## 1. Probar el comando manualmente primero

Antes de programarlo, ejecútalo a mano contra producción (o una copia) para
confirmar que corre sin errores:

```bash
cd /opt/gestionaguaApp/gestionaguaApp   # ajusta a la ruta real en el servidor
source ../venv/bin/activate
DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production python manage.py generar_cobros
```

Por defecto factura el período (mes) actual. Para regenerar o probar un mes
específico (por ejemplo, para un backfill):

```bash
DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production python manage.py generar_cobros --periodo 2026-06
```

El comando es idempotente: correrlo dos veces para el mismo período no
duplica cobros ni cortes.

## 2. Crear un script wrapper

Para no repetir variables de entorno en el crontab, crea un script, por
ejemplo `/opt/gestionaguaApp/scripts/generar_cobros.sh`:

```bash
#!/bin/bash
set -e
cd /opt/gestionaguaApp/gestionaguaApp
source ../venv/bin/activate
export DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production
python manage.py generar_cobros >> /var/log/gestionagua/generar_cobros.log 2>&1
```

```bash
chmod +x /opt/gestionaguaApp/scripts/generar_cobros.sh
mkdir -p /var/log/gestionagua
```

Ajusta las rutas (`/opt/gestionaguaApp`, `/var/log/gestionagua`) a como esté
organizado realmente el servidor Oracle.

## 3. Programar el cron

Editar el crontab del usuario que tiene permisos sobre el proyecto (no root,
salvo que el despliegue ya corra como root):

```bash
crontab -e
```

Agregar la siguiente línea para ejecutar el comando el **último día de cada
mes a las 23:00**:

```cron
0 23 28-31 * * [ "$(date -d tomorrow +\%d)" = "01" ] && /opt/gestionaguaApp/scripts/generar_cobros.sh
```

Esta expresión corre el script todos los días entre el 28 y el 31 a las
23:00, pero solo actúa si el día siguiente es el 1° del mes (es decir, si hoy
es efectivamente el último día del mes). Es la forma estándar de programar
"el último día de cada mes" con cron estándar, que no tiene un operador nativo
para eso.

Guardar y verificar que quedó registrado:

```bash
crontab -l
```

## 4. Verificar que corrió

Revisar el log después de la primera ejecución:

```bash
tail -n 50 /var/log/gestionagua/generar_cobros.log
```

Debería verse algo como:

```
Generando cobros para el período 2026-07...
Cobros generados: 950. Omitidos: 3.
Cortes generados: 4.
```

## Alertas por correo si el comando falla

Además del log por redirección de shell (`/var/log/gestionagua/generar_cobros.log`),
el comando escribe su propio log estructurado (con timestamp y nivel) en
`gestionaguaApp/logs/generar_cobros.log`, dentro del repo, independientemente
de cómo se invoque.

Si `generar_cobros` lanza una excepción a mitad de camino, además de quedar
registrada en ambos logs, se envía un correo a `ADMIN_ALERT_EMAIL` (por
defecto `arielplazasalinas@gmail.com`, configurable por variable de entorno)
con el traceback completo, y el comando termina con exit code distinto de
cero — así cron también deja constancia del fallo por su propio mecanismo.

El envío usa SMTP configurado por variables de entorno en el `.env` de
producción:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=cuenta-real-del-comite@gmail.com
EMAIL_HOST_PASSWORD=contraseña-de-aplicación-de-gmail
DEFAULT_FROM_EMAIL=cuenta-real-del-comite@gmail.com
ADMIN_ALERT_EMAIL=correo-a-quien-avisar@gmail.com
```

> `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` quedaron con un placeholder en
> `settings/production.py` porque todavía no existe una cuenta de Gmail real
> asignada a esto. Antes de depender de esta alerta en producción, genera una
> [contraseña de aplicación](https://myaccount.google.com/apppasswords) en la
> cuenta que se vaya a usar para enviar y configura las variables reales en el
> `.env` del servidor Oracle — mientras tanto, el intento de envío fallará
> (credenciales inválidas), quedará registrado en el log, pero no llegará el
> correo. Esto no afecta la generación de cobros en sí ni oculta el error
> original: el comando sigue terminando con código de error igual.

## Notas

- El comando asigna `numero_boleta` en formato `YYYY-NNNNN`, correlativo por
  año — se reinicia solo cuando cambia el año en el `periodo` facturado, no
  hace falta ninguna tarea adicional al 1° de enero.
- El cargo de reposición por corte ($50.000) se agrega automáticamente al
  cobro que corresponda si el socio tuvo un corte repuesto pendiente de
  facturar — no requiere intervención manual.
- Si necesitas correrlo fuera de horario (por ejemplo, tras corregir datos de
  lecturas) puedes ejecutar `generar_cobros --periodo YYYY-MM` manualmente en
  cualquier momento; es seguro repetirlo.
