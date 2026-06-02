# Instalar Ubuntu 24.04.2 en PicoCalc usando Luckfox Lyra B

Esta guía documenta el procedimiento real utilizado para instalar la imagen comunitaria `ubuntu-24.04.2-picocalc` en una **PicoCalc** usando una **Luckfox Lyra B**. La Lyra B tiene memoria SPI NAND onboard, pero para esta imagen de Ubuntu se usó una **tarjeta microSD de 64 GB** como almacenamiento principal.

El procedimiento no fue completamente lineal: aparecieron algunos errores relacionados con el modo `Maskrom`, la selección del almacenamiento y un fallo de transferencia al 19%. Esta versión de la guía incluye esos problemas y cómo se resolvieron.

---

## Punto de partida

Hardware usado:

* PicoCalc nueva.
* Luckfox Lyra B nueva.
* Tarjeta microSD SanDisk Ultra 64 GB microSDXC Class 10.
* PC con Linux.
* Cable USB-C de datos.
* Imagen comunitaria `ubuntu-24.04.2-picocalc`.

La tarjeta de 64 GB resultó adecuada para uso definitivo. La imagen requiere al menos 16 GB, pero para una instalación cómoda conviene usar 32 GB o más.

---

## Preparar la imagen en la PC

Primero se clona el repositorio:

```bash
git clone https://github.com/markbirss/ubuntu-24.04.2-picocalc.git
```

Entramos al directorio:

```bash
cd ubuntu-24.04.2-picocalc
```

Opcionalmente, se puede eliminar la carpeta `.git` para ahorrar espacio:

```bash
rm -fr .git/
```

Luego se entra al directorio de la imagen:

```bash
cd image
```

Se extrae el archivo comprimido:

```bash
7z x image.7z.001
```

Después de extraer, se entra a la carpeta de la versión:

```bash
cd [18Jun2025]
```

Dentro de esa carpeta deberían aparecer archivos como estos:

```text
boot.img
MiniLoaderAll.bin
parameter.txt
rootfs.img
sha256sums.txt
uboot.img
update.img
upgrade_tool
upgrade_tool_v2.17.zip
```

En nuestro caso, la salida fue:

```text
total 20G
-rw-r--r-- 1 ariel ariel 9,9M jun 18  2025 boot.img
-rw-r--r-- 1 ariel ariel 263K jun 18  2025 MiniLoaderAll.bin
-rw-r--r-- 1 ariel ariel  344 jun 18  2025 parameter.txt
-rw-r--r-- 1 ariel ariel 9,8G jun 18  2025 rootfs.img
-rw-rw-r-- 1 ariel ariel  481 jun 18  2025 sha256sums.txt
-rw-r--r-- 1 ariel ariel 4,0M jun 18  2025 uboot.img
-rw-r--r-- 1 ariel ariel 9,8G jun 18  2025 update.img
-rwxrwxr-x 1 ariel ariel 3,2M sep 19  2022 upgrade_tool
-rw-rw-r-- 1 ariel ariel 1,4M jul 21  2023 upgrade_tool_v2.17.zip
```

Se puede verificar la integridad de los archivos con:

```bash
sha256sum *
```

Los hashes esperados publicados en el README son:

```text
a4fbadbe374f01a6c86708eb9615fa679bf3db03fb8176f4933f6f2243ee464c  boot.img
3f43aecc1b5a43689586fe400226610ec03410308f5ce34349c9ae10c20ff82d  MiniLoaderAll.bin
05a8ebd2cc7627722af8b8c8007985989632d5ed6fafa38c2688ca70d7645e7b  parameter.txt
1f0ae484e717d80ab11fe3dc74cad10f5f374a93222b84357c59048a2819cb15  rootfs.img
143ce7fd34449b2ded2a1ac39b342652240115305c47690f8c9f590d90330b16  uboot.img
d84683d1443e6d3a046259f39e25541484a4a71f3f5582d266af0f62f7367ef2  update.img
```

---

## Identificar la microSD

Antes de hacer nada destructivo, se conectó la microSD a la PC y se ejecutó:

```bash
lsblk
```

La salida relevante fue:

```text
sdd           8:48   1  59,5G  0 disk 
└─sdd1        8:49   1  59,5G  0 part /media/ariel/0123-4567
```

Esto confirmó que la microSD era:

```text
/dev/sdd
```

De todos modos, en este procedimiento finalmente no se usó `dd`, porque los archivos extraídos no eran una imagen raw de tarjeta completa, sino un paquete para flashear con `upgrade_tool`.

---

## Preparar la Luckfox Lyra B

La microSD debe estar colocada en la Luckfox Lyra B durante el proceso.

Para entrar en modo de flasheo:

1. Desconectar la Lyra del USB.
2. Insertar la microSD.
3. Mantener presionado el botón `BOOT`.
4. Conectar la Lyra por USB-C a la PC.
5. Soltar `BOOT`.
6. Verificar el modo con:

```bash
sudo ./upgrade_tool LD
```

Al comienzo, la placa apareció así:

```text
List of rockusb connected(1)
DevNo=1	Vid=0x2207,Pid=0x350f,LocationID=15	Mode=Maskrom	SerialNo=
```

Esto indica que la Lyra está detectada, pero en modo `Maskrom`.

---

## Borrar la SPI NAND interna

Como la Lyra B tiene SPI NAND onboard, conviene borrarla para evitar que la placa intente arrancar desde la NAND interna en lugar de hacerlo desde la microSD.

Se ejecutó:

```bash
sudo ./upgrade_tool EF MiniLoaderAll.bin
```

La salida fue extensa, pero terminó correctamente:

```text
Loading loader...
Start to erase flash...
Download Boot Start
Download Boot Success
Wait For Maskrom Start
Wait For Maskrom Success
Test Device Start
Test Device Success
Get FlashInfo Start
Get FlashInfo Success
Prepare IDB Start
Prepare IDB Success
Erase IDB Start
Erase IDB Success
Reset Device Start
Reset Device Success
Wait For Maskrom Start
Wait For Maskrom Success
Download Boot Start
Download Boot Success
Wait For Maskrom Start
Wait For Maskrom Success
Test Device Start
Test Device Success
Get FlashInfo Start
Get FlashInfo Success
Erase Flash Start
Erase Flash... (100%)
Erase Flash Success
Reset Device Start
Erase flash ok.
```

Este paso fue exitoso.

---

## Primer problema: `SSD` no funciona todavía

Después de borrar la NAND, se intentó usar:

```bash
sudo ./upgrade_tool SSD
```

pero apareció el error:

```text
device doesn't have the feature,please do rcb command firstly
```

Entonces se intentó:

```bash
sudo ./upgrade_tool RCB
```

pero falló:

```text
Read capability Fail!
```

Esto ocurrió porque la placa seguía en `Maskrom` y todavía no tenía cargado un loader funcional para habilitar comandos como `RCB` o `SSD`.

---

## Cargar temporalmente el loader

Se probó:

```bash
sudo ./upgrade_tool DB MiniLoaderAll.bin
```

La primera vez respondió correctamente:

```text
Download boot ok.
```

Luego se verificó el modo:

```bash
sudo ./upgrade_tool LD
```

Durante una etapa todavía apareció como `Maskrom`:

```text
List of rockusb connected(1)
DevNo=1	Vid=0x2207,Pid=0x350f,LocationID=15	Mode=Maskrom	SerialNo=rockchip
```

Más adelante, después de desconectar y reconectar correctamente, apareció como `Loader`:

```text
List of rockusb connected(1)
DevNo=1	Vid=0x2207,Pid=0x350f,LocationID=15	Mode=Loader	SerialNo=2a9dfd2363bcabd0
```

Una vez que la placa ya está en `Loader`, no hay que volver a ejecutar `DB MiniLoaderAll.bin`. Si se hace, puede aparecer:

```text
The  Device did not support this operation!
```

Ese error es normal en este contexto: `DB` era necesario para pasar desde `Maskrom`, pero ya no corresponde cuando la placa está en `Loader`.

---

## Segundo problema: la imagen intenta grabarse en la SPI NAND

Se probó flashear directamente:

```bash
sudo ./upgrade_tool uf update.img
```

Esta vez el proceso comenzó, pero falló:

```text
Loading firmware...
Support Type:350F	FW Ver:8.1.00	FW Time:2025-06-18 18:36:43
Loader ver:1.01	Loader Time:2025-06-18 18:34:32
Start to upgrade firmware...
Test Device Start
Test Device Success
Check Chip Start
Check Chip Success
Get FlashInfo Start
Get FlashInfo Success
Prepare IDB Start
Prepare IDB Success
Download IDB Start
Download IDB Success
Download Firmware Start
Download Firmware Fail
Note:Image is larger than partition size in the firmware
```

Este error fue clave. Significa que `upgrade_tool` estaba intentando grabar la imagen de Ubuntu en la SPI NAND interna, que es demasiado pequeña para una imagen de casi 10 GB.

La solución fue cambiar el almacenamiento de destino.

---

## Leer capacidades con `RCB`

En modo `Loader`, se ejecutó:

```bash
sudo ./upgrade_tool RCB
```

Cuando funcionó correctamente, devolvió:

```text
Capability:15 6F 00 00 00 00 00 00 
Direct LBA:	enabled
First 4m Access:	enabled
Read Com Log:	enabled
Read Secure Mode:	enabled
New IDB:	enabled
Switch Storage:	enabled
```

La línea importante es:

```text
Switch Storage:	enabled
```

Eso confirma que ya se puede cambiar el destino de almacenamiento.

---

## Ver los dispositivos de almacenamiento disponibles

Se ejecutó:

```bash
sudo ./upgrade_tool SSD
```

La herramienta mostró:

```text
List of supported storage
No=1	FLASH
No=2	EMMC
No=3	SD
No=4	SD1
No=5	SPINOR
No=6	SPINAND(*)
No=7	RAM
No=8	USB
No=9	SATA
No=10	PCIE
```

El asterisco indicaba que estaba seleccionada la SPI NAND interna:

```text
No=6	SPINAND(*)
```

Eso explicaba el error anterior.

---

## Intento fallido: seleccionar `SD`

Parecía lógico elegir la opción `3`, porque decía `SD`.

Se probó:

```bash
sudo ./upgrade_tool SSD 3
```

pero falló:

```text
Error:Switch Storage failed!
```

Luego se probó en modo interactivo:

```bash
sudo ./upgrade_tool SSD
```

Cuando preguntó:

```text
Input No to switch,Quit press <Q>:
```

se ingresó:

```text
3
```

y volvió a fallar:

```text
Error:Switch Storage failed!
```

Conclusión: aunque `SD` aparecía listado, en este loader/placa no era el destino funcional para esta instalación.

---

## Solución: seleccionar `EMMC`, opción 2

En el hilo del foro se mencionaba usar la opción 2. Aunque aparecía como `EMMC`, en este caso fue la opción correcta.

Se ejecutó:

```bash
sudo ./upgrade_tool SSD
```

y cuando preguntó:

```text
Input No to switch,Quit press <Q>:
```

se ingresó:

```text
2
```

La herramienta respondió:

```text
Switch EMMC ok.
```

Luego se verificó repitiendo:

```bash
sudo ./upgrade_tool SSD
```

La salida mostró:

```text
List of supported storage
No=1	FLASH
No=2	EMMC(*)
No=3	SD
No=4	SD1
No=5	SPINOR
No=6	SPINAND
No=7	RAM
No=8	USB
No=9	SATA
No=10	PCIE
Input No to switch,Quit press <Q>:
```

Ahora el asterisco estaba en:

```text
No=2	EMMC(*)
```

Esto confirmó que el destino correcto estaba seleccionado.

Para salir sin cambiar nada, se ingresó:

```text
Q
```

---

## Primer intento de flasheo en `EMMC`: fallo al 19%

Con `EMMC(*)` seleccionado, se ejecutó:

```bash
sudo ./upgrade_tool uf update.img
```

El proceso comenzó:

```text
Loading firmware...
Support Type:350F	FW Ver:8.1.00	FW Time:2025-06-18 18:36:43
Loader ver:1.01	Loader Time:2025-06-18 18:34:32
Start to upgrade firmware...
Test Device Start
Test Device Success
Check Chip Start
Check Chip Success
Get FlashInfo Start
Get FlashInfo Success
Prepare IDB Start
Prepare IDB Success
Download IDB Start
Download IDB Success
Download Firmware Start
Download Image... (19%)
Download Firmware Fail
```

Este fallo ya no era por tamaño de partición. Probablemente fue una interrupción de transferencia, un problema de cable USB, puerto USB o estado inestable del loader.

Después de este fallo, se revisó si la placa seguía conectada:

```bash
sudo ./upgrade_tool LD
```

y respondió:

```text
List of rockusb connected(1)
DevNo=1	Vid=0x2207,Pid=0x350f,LocationID=15	Mode=Loader	SerialNo=2a9dfd2363bcabd0
```

Luego se intentó:

```bash
sudo ./upgrade_tool SSD
```

pero volvió a aparecer:

```text
device doesn't have the feature,please do rcb command firstly
```

Entonces se ejecutó:

```bash
sudo ./upgrade_tool RCB
```

En un primer intento falló:

```text
Read capability Fail!
```

Se probó cambiar o acomodar la conexión USB. En un momento la placa no fue detectada:

```text
List of rockusb connected(0)
```

Luego se reconectó correctamente y volvió a aparecer:

```text
List of rockusb connected(1)
DevNo=1	Vid=0x2207,Pid=0x350f,LocationID=15	Mode=Loader	SerialNo=2a9dfd2363bcabd0
```

Después de eso, `RCB` funcionó:

```bash
sudo ./upgrade_tool RCB
```

Salida:

```text
Capability:15 6F 00 00 00 00 00 00 
Direct LBA:	enabled
First 4m Access:	enabled
Read Com Log:	enabled
Read Secure Mode:	enabled
New IDB:	enabled
Switch Storage:	enabled
```

Se verificó otra vez el destino:

```bash
sudo ./upgrade_tool SSD
```

y se confirmó:

```text
No=2	EMMC(*)
```

---

## Flasheo final exitoso

Con la placa en `Loader`, `RCB` funcionando y `EMMC(*)` seleccionado, se repitió:

```bash
sudo ./upgrade_tool uf update.img
```

Esta vez el flasheo terminó correctamente:

```text
Loading firmware...
Support Type:350F	FW Ver:8.1.00	FW Time:2025-06-18 18:36:43
Loader ver:1.01	Loader Time:2025-06-18 18:34:32
Start to upgrade firmware...
Test Device Start
Test Device Success
Check Chip Start
Check Chip Success
Get FlashInfo Start
Get FlashInfo Success
Prepare IDB Start
Prepare IDB Success
Download IDB Start
Download IDB Success
Download Firmware Start
Download Image... (100%)
Download Firmware Success
Upgrade firmware ok.
```

Ese es el resultado esperado.

---

## Intento de reinicio

Después del flasheo exitoso, se intentó reiniciar con:

```bash
sudo ./upgrade_tool RD
```

pero la herramienta respondió:

```text
No found any rockusb device,please plug device in!
```

Esto no fue un problema. Después de `Upgrade firmware ok.`, la placa puede reiniciarse sola o dejar de exponerse como dispositivo RockUSB.

---

## Instalación física en la PicoCalc

Después del flasheo exitoso:

1. Desconectar la Luckfox Lyra B del USB.
2. Dejar la microSD puesta en la Lyra.
3. Apagar la PicoCalc.
4. Retirar baterías o alimentación.
5. Abrir la PicoCalc.
6. Retirar la Raspberry Pi Pico original.
7. Insertar la Luckfox Lyra B en el zócalo, respetando la orientación correcta.
8. Volver a alimentar la PicoCalc.
9. Encender.

Resultado:

```text
Booteo OK
```

La PicoCalc arrancó correctamente con Ubuntu 24.04.2 desde la Luckfox Lyra B.

---

# Resumen del procedimiento que funcionó

La secuencia efectiva, una vez extraída la imagen, fue:

```bash
sudo ./upgrade_tool LD
```

Si aparece en `Maskrom`, borrar la SPI NAND:

```bash
sudo ./upgrade_tool EF MiniLoaderAll.bin
```

Luego, si sigue en `Maskrom`, cargar loader:

```bash
sudo ./upgrade_tool DB MiniLoaderAll.bin
```

Verificar:

```bash
sudo ./upgrade_tool LD
```

Cuando aparezca:

```text
Mode=Loader
```

leer capacidades:

```bash
sudo ./upgrade_tool RCB
```

Verificar que aparezca:

```text
Switch Storage: enabled
```

Entrar al selector de storage:

```bash
sudo ./upgrade_tool SSD
```

Si aparece:

```text
No=6	SPINAND(*)
```

cambiar a opción 2:

```text
2
```

Debe responder:

```text
Switch EMMC ok.
```

Confirmar:

```bash
sudo ./upgrade_tool SSD
```

Debe aparecer:

```text
No=2	EMMC(*)
```

Salir con:

```text
Q
```

Flashear:

```bash
sudo ./upgrade_tool uf update.img
```

El resultado correcto es:

```text
Download Image... (100%)
Download Firmware Success
Upgrade firmware ok.
```

---

# Problemas encontrados y solución

## Error: `device doesn't have the feature,please do rcb command firstly`

Apareció al ejecutar:

```bash
sudo ./upgrade_tool SSD
```

Solución: ejecutar primero `RCB`, pero solo funciona si la placa está correctamente en `Loader`.

```bash
sudo ./upgrade_tool RCB
```

Si `RCB` falla, puede ser necesario cargar el loader con:

```bash
sudo ./upgrade_tool DB MiniLoaderAll.bin
```

o desconectar/reconectar la placa con `BOOT`.

---

## Error: `Read capability Fail!`

Apareció al ejecutar:

```bash
sudo ./upgrade_tool RCB
```

Causa probable: la placa seguía en `Maskrom`, o el loader quedó en estado inestable.

Solución: reconectar la placa, cargar `DB MiniLoaderAll.bin` si está en `Maskrom`, o verificar con:

```bash
sudo ./upgrade_tool LD
```

---

## Error: `Image is larger than partition size in the firmware`

Apareció al ejecutar:

```bash
sudo ./upgrade_tool uf update.img
```

Causa: la herramienta estaba intentando escribir la imagen en `SPINAND`, la memoria interna de la Lyra B, que es demasiado pequeña.

Solución: cambiar el storage con:

```bash
sudo ./upgrade_tool SSD
```

y seleccionar:

```text
2
```

hasta que aparezca:

```text
No=2	EMMC(*)
```

---

## Error: `Error:Switch Storage failed!` al elegir `SD`

Apareció al intentar:

```text
3
```

en el selector de storage.

Aunque `SD` parecía la opción lógica, en este caso no funcionó.

Solución: usar la opción `2`, que aparece como `EMMC`.

---

## Fallo al 19%

Apareció durante:

```bash
sudo ./upgrade_tool uf update.img
```

Salida:

```text
Download Image... (19%)
Download Firmware Fail
```

Causa probable: inestabilidad de conexión USB, puerto, cable o estado del loader.

Solución aplicada:

1. Verificar que la placa siga en `Loader`:

```bash
sudo ./upgrade_tool LD
```

2. Si `SSD` vuelve a pedir `RCB`, ejecutar:

```bash
sudo ./upgrade_tool RCB
```

3. Confirmar que el destino siga siendo:

```text
No=2	EMMC(*)
```

4. Repetir:

```bash
sudo ./upgrade_tool uf update.img
```

El segundo intento completó al 100%.

---

# Nota importante sobre la opción 2

Aunque la herramienta muestra:

```text
No=2	EMMC
No=3	SD
```

en esta instalación concreta la opción correcta fue:

```text
No=2	EMMC(*)
```

La opción `3 SD` apareció listada, pero no pudo seleccionarse. La opción `2 EMMC` fue la que permitió flashear correctamente la imagen grande y luego bootear la Lyra B en la PicoCalc.

Por eso, para esta combinación de **Luckfox Lyra B + imagen Ubuntu 24.04.2 PicoCalc + upgrade_tool**, el paso crítico es:

```text
Seleccionar storage 2 / EMMC
```

no `SD`.

---

# Estado final

La instalación terminó correctamente.

La salida final del flasheo fue:

```text
Download Image... (100%)
Download Firmware Success
Upgrade firmware ok.
```

Después de instalar la Luckfox Lyra B en la PicoCalc, el sistema arrancó correctamente.

Resultado:

```text
PicoCalc + Luckfox Lyra B + Ubuntu 24.04.2 = booteo OK
```
