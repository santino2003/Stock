from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["tkinter"],
    "include_files": [(r"C:\Users\santi\OneDrive\Escritorio\Stock - copia\regomaxultimo-firebase-adminsdk-wejo4-f535e92b5c.json", "regomaxultimo-firebase-adminsdk-wejo4-f535e92b5c.json"),(r"C:\Users\santi\OneDrive\Escritorio\Stock - copia\ubi.csv","ubi.csv"),(r"C:\Users\santi\OneDrive\Escritorio\Stock - copia\validaciones.csv","validaciones.csv"),(r"C:\Users\santi\OneDrive\Escritorio\Stock - copia\prod.csv","prod.csv"),(r"C:\Users\santi\OneDrive\Escritorio\Stock - copia\R.ico","R.ico"),(r"C:\Users\santi\OneDrive\Escritorio\Stock - copia\stock_historico.csv","stock_historico.csv")]

}

setup(
    name="Regomax",
    version="0.1",
    description="Una descripción de mi aplicación",
    options={"build_exe": build_exe_options},
    executables=[Executable("Regomax.py", base="Win32GUI", icon=r"C:\Users\santi\OneDrive\Escritorio\Stock - copia\R.ico")]
)