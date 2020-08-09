Mejoras

Backend, capa de servidor

Al conseguir los registros de la correspondiente unidad de estudio para cada red social, se inicia el proceso de análisis de factores emocionales, considerando un nivel de iteraciones apartir de la cantidad de factores estudiados y de registros en memoria. Las subrutinas de análisis estan construidas para desprender el resultado de la representación de un factor determinado para una lista registros entregados.

Si bien, este marco de trabajo ofrece facilidades para desprender un factor determinado en una lista de registros, el no considerar un método de análisis global de factores emocionales para un registro individual, implica un número de iteraciones considerablemente superior a su alternativa.

Como se puede apreciar, el número de iteraciones se reduce de forma considerable con un análisis factorial por registro, en lugar de un análisis de registros por factor emocional.

Teniendo en cuenta un análisis factorial de un gran número de registros, la implementación de estrategias de concurrencia y paralelización pueden resultar en una velocidad de cómputo mayor a raíz del consumo óptimo de recursos del servidor. Para esto es posible dividir la lista total de registros en tramos, que serán resueltos de forma particular por procesos específicos para los mismos, agilizando el análisis factorial. Esta forma de trabajo puede ampliarse a varias computadoras, asignando tramos específicos de la lista global de registros, donde cada una resolverá los mismos mediante procesos asíncronos subdividiendo su tramo asignado. Cabe mencionar que deben existir existir limitaciones para el acceso a memoria, tanto si se aplican estrategias de iteración con varios procesos o varias computadoras.

Finalmente, las estrategias de concurrencia y paralelización también pueden aplicarse al momento de obtener los registros en tiempo real, llenando una lista global de datos de forma asíncrona.

Frontend, capa de cliente

Al entregar los datos para su visualización, el panel de administración almacena los mismos en diferentes arreglos dependiendo de su procedencia, lo que brinda una mayor disponibilidad de los datos. Sin embargo, en términos de grandes números de registros, este proceso puede ocasionar la lentitud operativa del panel de administración, a raíz de un consumo mayor de recursos para preservar esta lista en memoria. Se sugiere establecer una paginación en conjunto con la capa de servidor para entregar un número limitado de registros asociados a un análisis factorial determinado. De esta forma, los datos serán solicitados en demanda, preservando en memoria solo los requeridos y no afectando los resultados finales del análisis.
