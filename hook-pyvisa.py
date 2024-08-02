from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('pyvisa')
datas_pyvisa_py, binaries_pyvisa_py, hiddenimports_pyvisa_py = collect_all('pyvisa_py')

datas += datas_pyvisa_py
binaries += binaries_pyvisa_py
hiddenimports += hiddenimports_pyvisa_py

# If needed, print the collected items for debugging
print("Datas:", datas)
print("Binaries:", binaries)
print("Hiddenimports:", hiddenimports)
