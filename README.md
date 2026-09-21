# TFG_Project

Proyecto de TFG: DISENO E IMPLEMENTACION DE UN CUADRO DE MANDO INTEGRAL PARA EL SOPORTE A LA TOMA DE DECISIONES EN EL SISTEMA DE EDUCACION PRIMARIA DE CATALUNA.

## Dataset

El dataset se distribuye comprimido en `Datos.zip` para evitar superar el limite de 100 MB por archivo de GitHub. El archivo comprimido contiene `Datos.csv`.

### Uso local

1. Descarga o clona este repositorio.
2. Descomprime `Datos.zip` en la raiz del proyecto.
3. Comprueba que `Datos.csv` se encuentra en la raiz del proyecto.

En Windows PowerShell puedes ejecutar:

```powershell
Expand-Archive -Path .\Datos.zip -DestinationPath . -Force
```

Despues de descomprimirlo, las herramientas del proyecto pueden trabajar con `Datos.csv` de forma local. El CSV descomprimido no debe volver a subirse al repositorio.
